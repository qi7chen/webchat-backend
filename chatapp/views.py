import os
import json
import uuid
import logging
import time
from datetime import datetime

import django.contrib.auth as auth
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_GET
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions, views
from rest_framework.response import Response
from openai import OpenAI


from chatapp.models import ChatMessage

logger = logging.getLogger(__name__)


def get_request_ip(request):
    for name in ['X-Forwarded-For', 'X-Real-IP']:
        real_ip = request.headers.get(name)
        if real_ip:
            return real_ip.split(',')[-1].strip()
    ip = request.META.get('REMOTE_ADDR')
    return ip or '??'


@require_http_methods(['GET', 'POST'])
def login(request):
    next = request.GET.get('next', '')
    args = json.loads(request.body)
    username = args.get('username') or ''
    password = args.get('password') or ''
    username = username.strip()
    password = password.strip()
    if username == '' or password == '':
        return HttpResponse(status=401, content='账号或密码错误')

    ip = get_request_ip(request)

    logger.info('%s(%s) login', username, ip)

    user = auth.authenticate(username=username, password=password)
    if user is None:
        return HttpResponse(status=401, content='账号与密码不匹配')

    auth.login(request, user)

    if next != '':
        return redirect(next)
    data = {'status': 'Success', 'username': username, 'token': str(user.auth_token)}
    return HttpResponse(status=200, content=json.dumps(data))


@login_required
@require_GET
def logout(request):
    ip = get_request_ip(request)
    logger.info('%s(%s) logged out', request.user.username, ip)
    user = request.user
    auth.logout(request)
    return redirect('userprofile:login')


class HomeView(View):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return render(request, 'home.html')


class ChatView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', '')
        )

    def load_conversation_messages(self, username: str, parent_message_id: str, messages: list) -> int:
        conversation_id = 0
        query_set = ChatMessage.objects.filter(user_name=username, chat_id=parent_message_id).values('conversation_id')
        for chat in query_set:
            conversation_id = chat['conversation_id']
            break
        if conversation_id != '':
            logger.debug('load conversation=%s by chat id=%s', conversation_id, parent_message_id)
            query_set = ChatMessage.objects.filter(user_name=username, conversation_id=conversation_id).order_by('created_at').values('role', 'text')
            for rs in query_set:
                messages.append({'role': rs['role'], 'content': rs['text']})

        return conversation_id

    def chat(self, user, data):
        messages = []

        system_message = data.get('systemMessage', '')
        if system_message != '':
            messages.append({'role': 'system', 'content': system_message})

        conversation_id = int(data.get('uuid', 0))
        parent_message_id = ''
        options = data.get('options', {})
        if len(options) > 0:
            parent_message_id = options.get('parentMessageId', '')
            if parent_message_id != '':
                conversation_id = self.load_conversation_messages(user.username, parent_message_id, messages)

        prompt = data.get('prompt', '')
        if prompt != '':
            messages.append({'role': 'user', 'content': prompt})

        if len(messages) == 0:
            return Response({'status': 'Error', 'message': 'No message to send'})

        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

        now = datetime.now()
        chat_ts = int(time.mktime(now.timetuple()))
        chat_c = {
            'created_at': now,
            'user_name': user.username,
            'chat_id': str(uuid.uuid4()),
            'model': '',
            'conversation_id': '',
            'role': 'user',
            'text': data.get('prompt', ''),
        }
        if conversation_id != 0:
            chat_c['conversation_id'] = conversation_id
        else:
            chat_c['conversation_id'] = chat_ts

        logger.info('create chat %s', json.dumps(messages, ensure_ascii=False))

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )

        if len(response.choices) == 0:
            return {'status': 'Error', 'message': 'No response from OpenAI'}

        choice = response.choices[0]
        chat_s = {
            'created_at': datetime.now(),
            'user_name': user.username,
            'chat_id': response.id,
            'model': response.model,
            'conversation_id': chat_c['conversation_id'],
            'detail': json.dumps({'prompt': prompt, 'options': options}, ensure_ascii=False)
        }

        if response.usage:
            chat_s['total_tokens'] = response.usage.total_tokens
        if choice.message:
            chat_s['role'] = choice.message.role
            chat_s['text'] = choice.message.content

        logger.info('chat response: %s', choice.to_json())

        cm = ChatMessage.objects.create(**chat_c)
        cm.save()
        cm = ChatMessage.objects.create(**chat_s)
        cm.save()

        return {
            'status': 'Success',
            'role': choice.message.role,
            'text': choice.message.content,
            'id': response.id,
            'parentMessageId': parent_message_id,
            'system_fingerprint': response.system_fingerprint,
            'detail': choice.to_dict(),
        }

    def chat_stream(self, user, data):
        messages = []

        prompt = data.get('prompt', '')
        if prompt == '':
            return {'status': 'Error', 'message': 'No prompt to send'}

        system_message = data.get('systemMessage', '')
        if system_message != '':
            messages.append({'role': 'system', 'content': system_message})

        conversation_id = int(data.get('uuid', 0))
        parent_message_id = ''
        options = data.get('options', {})
        if len(options) > 0:
            parent_message_id = options.get('parentMessageId', '')
            if parent_message_id != '':
                conversation_id = self.load_conversation_messages(user.username, parent_message_id, messages)

        messages.append({'role': 'user', 'content': prompt})

        if len(messages) == 0:
            return {'status': 'Error', 'message': 'No message to send'}

        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

        now = datetime.now()
        chat_ts = int(time.mktime(now.timetuple()))
        chat_c = {
            'created_at': now,
            'user_name': user.username,
            'chat_id': str(uuid.uuid4()),
            'model': model,
            'text': prompt,
            'conversation_id': '',
            'role': 'user',
        }
        if conversation_id != 0:
            chat_c['conversation_id'] = conversation_id
        else:
            chat_c['conversation_id'] = chat_ts

        logger.info('create chat %s', json.dumps(messages, ensure_ascii=False))

        cm = ChatMessage.objects.create(**chat_c)
        cm.save()

        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        chat_s = {
            'chat_id': '',
            'created_at': datetime.now(),
            'user_name': user.username,
            'model': model,
            'conversation_id': chat_c['conversation_id'],
            'role': 'assistant',
            'text': '',
            'detail': {},
        }

        for chunk in stream:
            # chat_s['role'] = choice.message.role
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    # logger.info("chunk : " + chunk.to_json())
                    if not chat_s['chat_id']:
                        chat_s['chat_id'] = chunk.id
                    chat_s['text'] += delta.content
                    ret = {
                        'status': 'Success',
                        'role': chat_s['role'],
                        'text': chat_s['text'],
                        'id': chunk.id,
                        'parentMessageId': parent_message_id,
                        'system_fingerprint': '',
                        'detail': {},
                    }
                    text = json.dumps(ret, ensure_ascii=False, sort_keys=True)
                    print('chunk text: ' + text)
                    logger.info('chunk text: %s', chat_s['text'])
                    yield text + '\n'  # delimiter for event-stream

        logger.info('chat response: %s', chat_s['text'])

        cm = ChatMessage.objects.create(**chat_s)
        cm.save()


    def post(self, request):
        data = request.data
        prompt = data.get('prompt', '')
        if prompt == '':
            return Response({'status': 'Error', 'message': 'No prompt to send'})

        # resp = self.chat(request.user, data)
        # return Response(resp)

        stream = self.chat_stream(request.user, data)
        resp = StreamingHttpResponse(stream, status=200, content_type='text/event-stream')
        resp.headers['X-Accel-Buffering'] = 'no'  # disable proxy buffering
        return resp


    def get(self, request):
        user = request.user
        conversations = {}
        query_set = ChatMessage.objects.filter(user_name=user.username).order_by('created_at').values(
            'created_at', 'chat_id', 'conversation_id', 'created_at', 'role', 'text', 'detail')
        for chat in query_set:
            if type(chat['detail']) is str:
                chat['detail'] = json.loads(chat['detail'])
            conversation_id = chat['conversation_id']
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            conversations[conversation_id].append(chat)

        # 转换为前端需要的格式
        data = {
            'usingContext': True,
            'history': [],
            'chat': []
        }
        for cid in conversations:
            chats = conversations[cid]
            front_chats = []
            history = {'title': '', 'uuid': 0, 'isEdit': False}
            # chats.sort()
            for chat in chats:
                cm = {
                    'datetime': chat['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    'id': chat['chat_id'],
                    'text': chat['text'],
                    'inversion': chat['role'] == 'user',
                    'conversationOptions': None,
                    'requestOptions': chat['detail'],
                    'error': False,
                    'loading': False,
                }
                if 'options' in chat['detail']:
                    if 'parentMessageId' in chat['detail']:
                        cm['conversationOptions'] = {
                            'parentMessageId': chat['detail']['parentMessageId']
                        }

                if chat['role'] == 'user' and history['title'] == '':
                    history['title'] = chat['text']
                    history['uuid'] = cid
                front_chats.append(cm)
            data['chat'].append({'uuid': history['uuid'], 'data': front_chats})
            data['history'].append(history)

        return Response({'status': 'Success', 'data': data})

    def delete(self, request):
        user = request.user
        data = request.data

        chat_id = data.get('chat_id', '')
        conversation_id = data.get('conversation_id', 0)  # 删除整个对话

        logger.info('delete chat id=%s, conversation=%s', chat_id, conversation_id)

        rs = None
        if conversation_id != '':
            rs = ChatMessage.objects.filter(user_name=user.username, conversation_id=conversation_id).delete()
        elif chat_id != '':
            rs = ChatMessage.objects.filter(user_name=user.username, chat_id=chat_id).delete()

        return Response({'status': 'Success', 'count': rs[0]})

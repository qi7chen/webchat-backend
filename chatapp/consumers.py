import os
import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from openai import OpenAI

class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', '')
        )

    async def connect(self):
        await self.accept()
        self.user = self.scope['user']

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        prompt = data.get('prompt', '')
        if prompt == '':
            self.close(code=4000, reason='Prompt is required')
            return

        options = data.get('option', {})
        system_message = options.get('systemMessage', 'You are a helpful assistant')
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        stream = self.client.chat.completions.create(
            model=model,
            stream=True,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            response_format={'type': 'text'},
        )
        text = ''
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    # logger.info("chunk : " + chunk.to_json())
                    text += delta.content
                    yield delta.content
        print('response text is: ' + text)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.send(text_data=json.dumps({"message": message}))

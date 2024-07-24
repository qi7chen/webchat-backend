from datetime import datetime
from django.test import TestCase
from chatapp.models import ChatMessage

class ChatModelTestCase(TestCase):
    def test_chat_model(self):
        now = datetime.now()
        chat_c = {
            'created_at': now,
            'user_name': 'admin',
            'chat_id': '1234567890',
            'model': 'gpt-3.5-turbo',
            'text': 'what is the meaning of life?',
            'conversation_id': '1234567890',
            'role': 'user',
        }
        chat = ChatMessage.objects.create(**chat_c)
        self.assertEqual(chat.created_at, now)
        self.assertEqual(chat.user_name, 'admin')
        self.assertEqual(chat.chat_id, '1234567890')
        self.assertEqual(chat.model, 'gpt-3.5-turbo')
        self.assertEqual(chat.text, 'what is the meaning of life?')
        self.assertEqual(chat.conversation_id, '1234567890')

class ChatViewTestCase(TestCase):

    def test_chat_view(self):
        response = self.client.get('/chat')
        self.assertEqual(response.status_code, 200)
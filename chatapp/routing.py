from django.urls import re_path
import chatapp.consumers as consumers


websocket_urlpatterns = [
    re_path(r"chat-ws/", consumers.ChatConsumer.as_asgi()),
]

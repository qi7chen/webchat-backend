from django.urls import path
import gptchat.views as views

app_name = 'gptchat'

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('chat-process', views.ChatView.as_view(http_method_names=['post']), name='chat-process'),
    path('chat', views.ChatView.as_view(), name='chat'),
    path('chat-stream', views.ChatStreamView.as_view(), name='chat-stream'),
]

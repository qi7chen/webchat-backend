from django.urls import path
from django.views.decorators.cache import never_cache
import chatapp.views as views

app_name = 'chatapp'

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('chat-process', never_cache(views.ChatView.as_view(http_method_names=['post'])), name='chat-process'),
    path('chat-stream', never_cache(views.ChatStreamView.as_view()), name='chat-stream'),
]

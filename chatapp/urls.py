from django.urls import path
from django.views.decorators.cache import never_cache
import chatapp.views as views

app_name = 'chatapp'

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('chat-completion', never_cache(views.ChatView.as_view(http_method_names=['post'])), name='chat-completion'),
    path('chat-process', never_cache(views.ChatStreamView.as_view(http_method_names=['post'])), name='chat-process'),
    path('chat', views.ChatStreamView.as_view(http_method_names=['get', 'delete']), name='chat'),
]

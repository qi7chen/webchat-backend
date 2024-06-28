from django.db import models


class ChatMessage(models.Model):
    class Meta:
        index_together = [('user_name', 'conversation_id')]

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    chat_id = models.CharField(max_length=100, unique=True)      # 区分每条单独的chat消息
    user_name = models.CharField(max_length=100, default='')
    conversation_id = models.BigIntegerField(default=0)  # 区分每个对话
    model = models.CharField(max_length=50, default='')
    role = models.CharField(max_length=50, default='')
    text = models.TextField(default='')
    total_tokens = models.IntegerField(default=0)
    detail = models.JSONField(max_length=2500, default=dict)

# Web Chat Backend

聊天机器人服务，基于OpenAI GPT-3.5模型。

### 如何运行

#### 初始安装

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 创建数据库
python manage.py migrate

# 创建管理员
python manage.py createsuperuser
```


* 打开`http://localhost:3002/admin`页面，登录取得token
* 发起请求的HTTP header增加 `Authorization : Token your_token`
* 
```bash
curl -X POST http://localhost:3002/api/chat-process 
    -H 'Authorization: Token your_token'
    -d '{"prompt": "chatgpt可以做什么"}'
```
```javascript
// example output
{
    "role": "assistant",
    "text": "Hello! How can I assist you today?",
    "id": "chatcmpl-9WOuuLmWdv6nuiCuQojM3me4xFqkL",
    "parentMessageId": "",
    "system_fingerprint": null,
    "detail": {
        "id": "chatcmpl-9WOuuLmWdv6nuiCuQojM3me4xFqkL",
        "object": "chat.completion",
        "created": 1717509304,
        "model": "gpt-3.5-turbo-0125"
    }
}
```

```

####  接口说明

 接口URL         | 方法           | 用途
 ---------------|--------------|------
 /api/chat  | GET / DELETE |  拉取、删除聊天记录
 /api/chat-completion | POST         | 聊天对话（非stream)
 /api/chat-process | POST         | 流式聊天对话
 
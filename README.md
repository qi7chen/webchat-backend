# Web Chat GPT

聊天机器人服务，基于OpenAI GPT-3.5模型。

### 如何运行

#### 初始安装

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 创建数据库（默认sqlite）
python manage.py migrate

# 创建管理员(默认admin:123456)
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

#### 本地docker运行

```
docker compose up -d --build
```
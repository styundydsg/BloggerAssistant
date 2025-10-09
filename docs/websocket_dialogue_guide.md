# WebSocket对话使用指南

## 概述

本项目提供了一个完整的WebSocket联系服务，支持实时对话功能。WebSocket服务器运行在 `ws://127.0.0.1:8080/contact`，支持多种消息类型进行对话。

## 消息类型

### 1. 连接建立 (connection_established)
- **触发**: 客户端连接成功后自动发送
- **用途**: 确认连接成功，返回客户端ID

```json
{
  "type": "connection_established",
  "message": "WebSocket连接已建立",
  "client_id": "uuid-string",
  "timestamp": "2025-01-01T12:00:00"
}
```

### 2. 联系请求 (contact_request)
- **用途**: 发起联系请求，通知博主
- **必需字段**: message, timestamp, userAgent

```json
{
  "type": "contact_request",
  "message": "用户消息内容",
  "timestamp": "2025-01-01T12:00:00",
  "userAgent": "浏览器信息"
}
```

### 3. 聊天消息 (chat_message)
- **用途**: 实时对话消息
- **必需字段**: message, timestamp

```json
{
  "type": "chat_message",
  "message": "你好，我想咨询一些问题",
  "timestamp": "2025-01-01T12:00:00"
}
```

### 4. 心跳检测 (ping/pong)
- **用途**: 保持连接活跃
- **请求**: ping
- **响应**: pong

```json
// 客户端发送
{"type": "ping"}

// 服务器响应
{
  "type": "pong",
  "timestamp": "2025-01-01T12:00:00"
}
```

## 对话流程

### 步骤1: 启动WebSocket服务器

```bash
# 方法1: 直接运行
python api/tcp_contact.py

# 方法2: 从代码中启动
from api.tcp_contact import run_contact_server
run_contact_server()
```

### 步骤2: 客户端连接和对话

#### Python客户端示例

```python
import asyncio
import websockets
import json
from datetime import datetime

async def chat_with_websocket():
    """与WebSocket服务器进行对话"""
    
    try:
        # 连接WebSocket服务器
        async with websockets.connect('ws://127.0.0.1:8080/contact') as websocket:
            print("✅ 连接成功")
            
            # 监听服务器消息
            async def listen_messages():
                async for message in websocket:
                    data = json.loads(message)
                    print(f"🤖 服务器回复: {data.get('message', '')}")
            
            # 启动消息监听
            listener = asyncio.create_task(listen_messages())
            
            # 发送联系请求
            contact_msg = {
                "type": "contact_request",
                "message": "你好，我想咨询技术问题",
                "timestamp": datetime.now().isoformat(),
                "userAgent": "Python客户端"
            }
            await websocket.send(json.dumps(contact_msg))
            print("📤 已发送联系请求")
            
            # 等待确认
            await asyncio.sleep(1)
            
            # 开始对话
            messages = [
                "你好，这个博客系统是怎么搭建的？",
                "能介绍一下使用的技术栈吗？",
                "如何部署到生产环境？"
            ]
            
            for msg in messages:
                chat_msg = {
                    "type": "chat_message",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(chat_msg))
                print(f"💬 发送: {msg}")
                await asyncio.sleep(2)  # 等待回复
                
            # 保持连接一段时间
            await asyncio.sleep(5)
            listener.cancel()
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")

# 运行对话
asyncio.run(chat_with_websocket())
```

#### JavaScript前端示例

```javascript
// 建立WebSocket连接
const ws = new WebSocket('ws://127.0.0.1:8080/contact');

ws.onopen = () => {
    console.log('WebSocket连接已建立');
    
    // 发送联系请求
    ws.send(JSON.stringify({
        type: 'contact_request',
        message: '用户前端连接测试',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到服务器消息:', data);
    
    // 根据消息类型处理
    switch(data.type) {
        case 'connection_established':
            console.log('连接确认:', data.message);
            break;
        case 'contact_request_received':
            console.log('联系请求已收到');
            break;
        case 'chat_message':
            console.log('AI回复:', data.message);
            // 在界面上显示消息
            displayMessage(data.message, 'assistant');
            break;
        case 'error':
            console.error('错误:', data.message);
            break;
    }
};

ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
};

ws.onclose = () => {
    console.log('WebSocket连接已关闭');
};

// 发送聊天消息的函数
function sendChatMessage(message) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'chat_message',
            message: message,
            timestamp: new Date().toISOString()
        }));
    } else {
        console.error('WebSocket未连接');
    }
}

// 示例：发送消息
sendChatMessage('你好，我想了解这个项目');
```

### 步骤3: 服务器响应处理

服务器会对不同类型的消息做出相应响应：

1. **contact_request**: 返回 `contact_request_received` 确认
2. **chat_message**: 返回 `chat_message_received` 确认 + AI回复 `chat_message`
3. **ping**: 返回 `pong` 响应

## 高级功能

### 1. 集成AI问答系统

当前的AI回复是基础实现，可以集成现有的问答系统：

```python
async def generate_ai_response(self, message: str) -> str:
    """集成深度问答系统的AI回复"""
    try:
        # 调用现有的问答系统
        from lib.modules.qa_chain import get_qa_response
        response = await get_qa_response(message)
        return response
    except Exception as e:
        logger.error(f"AI回复生成失败: {e}")
        return "抱歉，我暂时无法处理您的请求，请稍后再试。"
```

### 2. 消息持久化

可以添加消息存储功能：

```python
async def save_chat_message(self, client_id: str, message: str, sender: str):
    """保存聊天消息到数据库"""
    # 实现消息存储逻辑
    pass
```

### 3. 多客户端管理

支持多个客户端同时连接：

```python
# 广播消息给所有客户端
async def broadcast_message(self, message: dict):
    """向所有连接的客户端广播消息"""
    for client_id, websocket in self.connected_clients.items():
        try:
            await websocket.send(json.dumps(message))
        except:
            # 移除断开连接的客户端
            del self.connected_clients[client_id]
```

## 错误处理

### 常见错误及解决方案

1. **连接拒绝**: 检查服务器是否启动，端口是否被占用
2. **消息格式错误**: 确保发送的是有效的JSON格式
3. **连接超时**: 定期发送ping消息保持连接活跃
4. **服务器重启**: 实现重连机制

### 重连机制示例

```javascript
function connectWebSocket() {
    const ws = new WebSocket('ws://127.0.0.1:8080/contact');
    
    ws.onclose = () => {
        console.log('连接断开，5秒后重连...');
        setTimeout(connectWebSocket, 5000);
    };
    
    // ... 其他事件处理
}
```

## 部署建议

### 生产环境配置

1. **使用wss协议**: 在生产环境使用安全的WebSocket连接
2. **负载均衡**: 多个WebSocket服务器实例
3. **会话管理**: 实现用户会话和认证
4. **监控日志**: 记录连接和消息统计

### Nginx配置示例

```nginx
location /websocket/ {
    proxy_pass http://websocket_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}
```

## 测试验证

使用提供的测试脚本验证功能：

```bash
python test/websocket_contact_test.py
```

这个指南提供了完整的WebSocket对话使用说明，包括连接建立、消息发送、响应处理和错误处理等完整流程。

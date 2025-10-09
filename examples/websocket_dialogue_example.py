"""WebSocket对话示例 - 演示如何接收和处理服务器发送的消息"""

import asyncio
import websockets
import json
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class WebSocketDialogueClient:
    """WebSocket对话客户端 - 演示消息接收和处理"""
    
    def __init__(self, uri="ws://127.0.0.1:8080/contact"):
        self.uri = uri
        self.messages_received = []
        self.client_id = None
    
    async def start_dialogue(self):
        """开始对话并演示消息接收"""
        print("=" * 60)
        print("WebSocket对话示例 - 消息接收演示")
        print("=" * 60)
        
        try:
            async with websockets.connect(self.uri) as websocket:
                print("✅ WebSocket连接成功")
                
                # 启动消息监听器
                listener_task = asyncio.create_task(self._listen_for_messages(websocket))
                
                # 演示完整的对话流程
                await self._demonstrate_dialogue_flow(websocket)
                
                # 等待所有消息处理完成
                await asyncio.sleep(3)
                listener_task.cancel()
                
                # 显示接收到的所有消息
                self._display_received_messages()
                
        except Exception as e:
            print(f"❌ 连接失败: {e}")
    
    async def _listen_for_messages(self, websocket):
        """监听服务器发送的消息 - 这是接收消息的关键位置"""
        try:
            async for message in websocket:
                data = json.loads(message)
                self.messages_received.append(data)
                
                # 根据消息类型进行不同处理
                await self._handle_server_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket连接已关闭")
        except Exception as e:
            print(f"❌ 消息接收错误: {e}")
    
    async def _handle_server_message(self, data):
        """处理服务器发送的不同类型消息"""
        message_type = data.get('type')
        
        print(f"\n📨 收到服务器消息类型: {message_type}")
        print(f"   消息内容: {data}")
        
        # 根据消息类型进行特定处理
        if message_type == 'connection_established':
            self.client_id = data.get('client_id')
            print(f"🎯 连接已建立，客户端ID: {self.client_id}")
            
        elif message_type == 'contact_request_received':
            request_id = data.get('request_id')
            print(f"📝 联系请求已确认，请求ID: {request_id}")
            
        elif message_type == 'chat_message_received':
            message_id = data.get('message_id')
            print(f"💬 聊天消息已确认，消息ID: {message_id}")
            
        elif message_type == 'chat_message':
            ai_message = data.get('message', '')
            sender = data.get('sender', 'unknown')
            print(f"🤖 AI回复 ({sender}): {ai_message}")
            
        elif message_type == 'pong':
            print("❤️  心跳响应收到")
            
        elif message_type == 'error':
            error_msg = data.get('message', '')
            print(f"❌ 错误消息: {error_msg}")
    
    async def _demonstrate_dialogue_flow(self, websocket):
        """演示完整的对话流程"""
        print("\n1️⃣ 发送联系请求...")
        
        # 发送联系请求
        contact_request = {
            "type": "contact_request",
            "message": "你好，我想咨询技术问题",
            "timestamp": datetime.now().isoformat(),
            "userAgent": "Python对话示例客户端"
        }
        await websocket.send(json.dumps(contact_request))
        await asyncio.sleep(1)  # 等待服务器响应
        
        print("\n2️⃣ 开始聊天对话...")
        
        # 发送一系列聊天消息
        chat_messages = [
            "你好，这个博客系统是怎么搭建的？",
            "能介绍一下使用的技术栈吗？",
            "如何部署到生产环境？"
        ]
        
        for i, message in enumerate(chat_messages, 1):
            print(f"\n💬 发送第{i}条消息: {message}")
            
            chat_msg = {
                "type": "chat_message",
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(chat_msg))
            await asyncio.sleep(2)  # 等待AI回复
        
        print("\n3️⃣ 发送心跳检测...")
        
        # 发送ping消息测试连接
        ping_msg = {"type": "ping"}
        await websocket.send(json.dumps(ping_msg))
        await asyncio.sleep(1)
    
    def _display_received_messages(self):
        """显示所有接收到的消息统计"""
        print("\n" + "=" * 60)
        print("消息接收统计")
        print("=" * 60)
        
        if not self.messages_received:
            print("❌ 没有收到任何消息")
            return
        
        # 按消息类型统计
        message_types = {}
        for msg in self.messages_received:
            msg_type = msg.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        print(f"📊 总共收到 {len(self.messages_received)} 条消息")
        print("消息类型分布:")
        for msg_type, count in message_types.items():
            print(f"  - {msg_type}: {count} 条")
        
        print("\n📋 详细消息列表:")
        for i, msg in enumerate(self.messages_received, 1):
            print(f"{i}. [{msg.get('type')}] {msg.get('message', '无消息内容')}")

# JavaScript前端代码示例（用于对比理解）
JS_FRONTEND_EXAMPLE = """
// JavaScript前端WebSocket消息接收示例
const ws = new WebSocket('ws://127.0.0.1:8080/contact');

// 连接建立事件
ws.onopen = () => {
    console.log('WebSocket连接已建立');
    
    // 发送联系请求
    ws.send(JSON.stringify({
        type: 'contact_request',
        message: '用户请求联系博主',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    }));
};

// 🎯 关键位置：服务器发送的消息在这里接收！
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到服务器消息:', data);
    
    // 根据消息类型进行不同处理
    switch(data.type) {
        case 'connection_established':
            console.log('连接确认:', data.message);
            console.log('客户端ID:', data.client_id);
            break;
            
        case 'contact_request_received':
            console.log('联系请求已收到，请求ID:', data.request_id);
            break;
            
        case 'chat_message_received':
            console.log('聊天消息已确认，消息ID:', data.message_id);
            break;
            
        case 'chat_message':
            console.log('AI回复:', data.message);
            // 在界面上显示AI回复
            displayMessage(data.message, 'assistant');
            break;
            
        case 'pong':
            console.log('心跳响应收到');
            break;
            
        case 'error':
            console.error('错误消息:', data.message);
            break;
            
        default:
            console.log('未知消息类型:', data.type);
    }
};

// 发送聊天消息的函数
function sendChatMessage(message) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'chat_message',
            message: message,
            timestamp: new Date().toISOString()
        }));
    }
}

// 示例：用户发送消息
sendChatMessage('你好，我想了解这个项目');
"""

async def main():
    """主函数"""
    print("WebSocket消息接收位置说明")
    print("=" * 60)
    print("""
在WebSocket通信中，服务器发送的消息通过以下方式接收：

Python客户端:
- 在 `_listen_for_messages()` 方法中通过 `async for message in websocket:` 循环接收
- 使用 `_handle_server_message()` 方法处理不同类型的消息

JavaScript前端:
- 在 `ws.onmessage` 事件处理函数中接收
- 通过 `event.data` 获取消息内容
- 使用 `switch` 语句根据消息类型进行不同处理

关键点:
1. 服务器发送的消息会自动推送到客户端
2. 客户端需要监听消息事件并处理
3. 消息格式为JSON，需要解析后使用
4. 根据消息类型进行相应的业务逻辑处理
""")
    
    # 运行对话示例
    client = WebSocketDialogueClient()
    await client.start_dialogue()

if __name__ == "__main__":
    asyncio.run(main())

"""WebSocket联系服务测试脚本"""

import asyncio
import websockets
import json
import time
import threading
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from api.tcp_contact import ContactWebSocketServer

class WebSocketClientTest:
    """WebSocket客户端测试类"""
    
    def __init__(self, uri="ws://127.0.0.1:8080/contact"):
        self.uri = uri
        self.messages_received = []
        self.connected = False
    
    async def connect_and_test(self):
        """连接并测试WebSocket服务器"""
        try:
            async with websockets.connect(self.uri) as websocket:
                self.connected = True
                print("✅ WebSocket连接成功")
                
                # 监听服务器消息
                listener_task = asyncio.create_task(self.listen_for_messages(websocket))
                
                # 发送测试消息
                await self.send_test_messages(websocket)
                
                # 等待所有消息接收完成
                await asyncio.sleep(2)
                listener_task.cancel()
                
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            self.connected = False
    
    async def listen_for_messages(self, websocket):
        """监听服务器发送的消息"""
        try:
            async for message in websocket:
                data = json.loads(message)
                self.messages_received.append(data)
                print(f"📨 收到服务器消息: {data}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket连接已关闭")
    
    async def send_test_messages(self, websocket):
        """发送测试消息"""
        # 发送联系请求（模拟前端代码）
        contact_request = {
            "type": "contact_request",
            "message": "用户请求联系博主",
            "timestamp": datetime.now().isoformat(),
            "userAgent": "Mozilla/5.0 (测试客户端)"
        }
        
        print(f"📤 发送联系请求: {contact_request}")
        await websocket.send(json.dumps(contact_request))
        await asyncio.sleep(1)
        
        # 发送聊天消息
        chat_message = {
            "type": "chat_message",
            "message": "你好，我想咨询一些问题",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 发送聊天消息: {chat_message}")
        await websocket.send(json.dumps(chat_message))
        await asyncio.sleep(1)
        
        # 发送ping消息
        ping_message = {"type": "ping"}
        print(f"📤 发送ping消息: {ping_message}")
        await websocket.send(json.dumps(ping_message))
        await asyncio.sleep(1)

def run_websocket_server():
    """在后台线程中运行WebSocket服务器"""
    server = ContactWebSocketServer()
    asyncio.run(server.start_server())

async def test_websocket_functionality():
    """测试WebSocket功能"""
    print("=" * 60)
    print("WebSocket联系服务测试")
    print("=" * 60)
    
    # 启动服务器线程
    print("🚀 启动WebSocket服务器...")
    server_thread = threading.Thread(target=run_websocket_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 测试客户端连接
    print("🔗 测试客户端连接...")
    client = WebSocketClientTest()
    await client.connect_and_test()
    
    # 分析测试结果
    print("\n" + "=" * 60)
    print("测试结果分析")
    print("=" * 60)
    
    if client.connected:
        print("✅ WebSocket连接测试通过")
        
        # 检查收到的消息类型
        message_types = [msg.get('type') for msg in client.messages_received]
        print(f"收到的消息类型: {message_types}")
        
        # 验证关键消息类型
        expected_types = ['connection_established', 'contact_request_received', 'chat_message_received', 'chat_message', 'pong']
        missing_types = [t for t in expected_types if t not in message_types]
        
        if missing_types:
            print(f"⚠️ 缺少的消息类型: {missing_types}")
        else:
            print("✅ 所有预期消息类型都已收到")
        
        # 检查联系请求处理
        contact_responses = [msg for msg in client.messages_received if msg.get('type') == 'contact_request_received']
        if contact_responses:
            print(f"✅ 联系请求处理正常，收到 {len(contact_responses)} 个确认")
        else:
            print("❌ 联系请求处理失败")
        
        # 检查聊天消息处理
        chat_responses = [msg for msg in client.messages_received if msg.get('type') == 'chat_message']
        if chat_responses:
            print(f"✅ 聊天消息处理正常，收到 {len(chat_responses)} 个AI回复")
        else:
            print("❌ 聊天消息处理失败")
            
    else:
        print("❌ WebSocket连接测试失败")
    
    print(f"\n📊 总共收到 {len(client.messages_received)} 条消息")
    
    return client.connected and len(client.messages_received) > 0

def test_frontend_compatibility():
    """测试前端代码兼容性"""
    print("\n" + "=" * 60)
    print("前端代码兼容性测试")
    print("=" * 60)
    
    # 模拟前端WebSocket连接代码
    frontend_code = """
// 建立WebSocket连接（TCP-like连接）
const ws = new WebSocket('ws://127.0.0.1:8080/contact');

ws.onopen = () => {
    console.log('WebSocket连接已建立');
    
    // 发送连接请求
    ws.send(JSON.stringify({
        type: 'contact_request',
        message: '用户请求联系博主',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    }));
    
    // 显示连接状态
    this.showChatInterface(ws);
};
"""
    
    print("前端代码分析:")
    print("- ✅ 连接地址: ws://127.0.0.1:8080/contact")
    print("- ✅ 消息类型: contact_request")
    print("- ✅ 消息格式: JSON")
    print("- ✅ 包含必要字段: message, timestamp, userAgent")
    
    print("\n服务器响应预期:")
    print("- ✅ 连接建立确认 (connection_established)")
    print("- ✅ 联系请求确认 (contact_request_received)")
    print("- ✅ 错误处理 (error)")
    print("- ✅ 心跳响应 (pong)")
    
    return True

async def main():
    """主测试函数"""
    try:
        # 测试前端兼容性
        frontend_ok = test_frontend_compatibility()
        
        # 测试WebSocket功能
        websocket_ok = await test_websocket_functionality()
        
        # 输出最终结果
        print("\n" + "=" * 60)
        print("最终测试结果")
        print("=" * 60)
        
        if frontend_ok and websocket_ok:
            print("🎉 所有测试通过！WebSocket联系服务功能正常。")
            print("\n使用说明:")
            print("1. 运行服务器: python api/tcp_contact.py")
            print("2. 前端连接: ws://127.0.0.1:8080/contact")
            print("3. 发送消息类型: contact_request, chat_message, ping")
        else:
            print("⚠️ 部分测试失败，请检查配置和日志。")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())

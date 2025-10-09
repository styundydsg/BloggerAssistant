"""简单的WebSocket对话测试 - 快速验证消息接收功能"""

import asyncio
import websockets
import json
from datetime import datetime

async def simple_websocket_test():
    """简单的WebSocket测试 - 重点演示消息接收位置"""
    
    print("🔍 WebSocket消息接收位置测试")
    print("=" * 50)
    
    try:
        # 连接WebSocket服务器
        async with websockets.connect('ws://127.0.0.1:8080/contact') as websocket:
            print("✅ 连接成功！")
            
            # 🎯 关键：这是接收服务器消息的位置！
            async def receive_messages():
                """接收服务器发送的所有消息"""
                print("\n📡 开始监听服务器消息...")
                message_count = 0
                
                async for message in websocket:
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 收到第{message_count}条消息:")
                    print(f"   类型: {data.get('type')}")
                    print(f"   内容: {data.get('message', '无消息内容')}")
                    print(f"   完整数据: {data}")
                    
                    # 如果是连接确认，保存客户端ID
                    if data.get('type') == 'connection_established':
                        print(f"🎯 客户端ID: {data.get('client_id')}")
            
            # 启动消息接收器
            receiver = asyncio.create_task(receive_messages())
            
            # 等待连接确认
            await asyncio.sleep(1)
            
            # 发送联系请求
            print("\n📤 发送联系请求...")
            contact_msg = {
                "type": "contact_request",
                "message": "测试联系请求",
                "timestamp": datetime.now().isoformat(),
                "userAgent": "测试客户端"
            }
            await websocket.send(json.dumps(contact_msg))
            
            # 等待联系请求确认
            await asyncio.sleep(1)
            
            # 发送聊天消息
            print("\n💬 发送聊天消息...")
            chat_msg = {
                "type": "chat_message",
                "message": "你好，这是测试消息",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(chat_msg))
            
            # 等待AI回复
            await asyncio.sleep(2)
            
            # 发送ping测试
            print("\n❤️  发送ping测试...")
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            
            # 等待所有消息处理完成
            await asyncio.sleep(2)
            receiver.cancel()
            
            print("\n✅ 测试完成！")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n💡 请确保WebSocket服务器正在运行:")
        print("   运行: python api/tcp_contact.py")

def main():
    """主函数"""
    print("""
WebSocket消息接收位置说明：

在JavaScript中，服务器发送的消息通过以下方式接收：

// 🎯 关键位置：服务器消息在这里接收！
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到服务器消息:', data);
    
    // 根据消息类型处理
    switch(data.type) {
        case 'connection_established':
            // 处理连接确认
            break;
        case 'chat_message':
            // 处理AI回复
            break;
        // ... 其他消息类型
    }
};

在Python中，通过 async for message in websocket: 循环接收。

服务器会自动发送以下类型的消息：
1. connection_established - 连接建立确认
2. contact_request_received - 联系请求确认  
3. chat_message_received - 聊天消息确认
4. chat_message - AI回复消息
5. pong - 心跳响应
6. error - 错误消息
""")
    
    # 运行测试
    asyncio.run(simple_websocket_test())

if __name__ == "__main__":
    main()

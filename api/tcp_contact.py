"""WebSocket联系服务 - 处理前端联系请求"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactWebSocketServer:
    """WebSocket联系服务器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.contact_requests: Dict[str, Dict[str, Any]] = {}
    
    async def handle_contact_request(self, websocket):
        """处理WebSocket连接请求"""
        client_id = str(uuid.uuid4())
        self.connected_clients[client_id] = websocket
        
        try:
            logger.info(f"客户端 {client_id} 已连接")
            
            # 发送连接确认
            await websocket.send(json.dumps({
                "type": "connection_established",
                "message": "WebSocket连接已建立",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            # 处理消息
            async for message in websocket:
                await self.handle_message(client_id, message, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_id} 断开连接")
        except Exception as e:
            logger.error(f"处理客户端 {client_id} 时出错: {e}")
        finally:
            # 清理连接
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
    
    async def handle_message(self, client_id: str, message: str, websocket):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            logger.info(f"收到来自 {client_id} 的消息类型: {message_type}")
            
            if message_type == "contact_request":
                await self.handle_contact_request_message(client_id, data, websocket)
            elif message_type == "chat_message":
                await self.handle_chat_message(client_id, data, websocket)
            elif message_type == "ping":
                await self.handle_ping(client_id, websocket)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"未知的消息类型: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "消息格式错误，必须是有效的JSON",
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"处理消息时出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def handle_contact_request_message(self, client_id: str, data: Dict[str, Any], websocket):
        """处理联系请求消息"""
        request_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 保存联系请求
        self.contact_requests[request_id] = {
            "client_id": client_id,
            "request_data": data,
            "timestamp": timestamp,
            "status": "received"
        }
        
        logger.info(f"收到联系请求 {request_id} 来自客户端 {client_id}")
        
        # 发送确认响应
        await websocket.send(json.dumps({
            "type": "contact_request_received",
            "message": "联系请求已收到，博主将尽快回复您",
            "request_id": request_id,
            "timestamp": timestamp,
            "status": "received"
        }))
        
        # 这里可以添加通知逻辑，比如发送邮件给博主
        await self.notify_blogger(request_id, data)
    
    async def handle_chat_message(self, client_id: str, data: Dict[str, Any], websocket):
        """处理聊天消息"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 记录聊天消息
        logger.info(f"收到聊天消息 {message_id} 来自客户端 {client_id}: {data.get('message', '')}")
        
        # 发送消息确认
        await websocket.send(json.dumps({
            "type": "chat_message_received",
            "message": "消息已收到",
            "message_id": message_id,
            "timestamp": timestamp
        }))
        
        # 这里可以添加AI回复逻辑
        ai_response = await self.generate_ai_response(data.get("message", ""))
        
        # 发送AI回复
        await websocket.send(json.dumps({
            "type": "chat_message",
            "message": ai_response,
            "sender": "assistant",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def handle_ping(self, client_id: str, websocket):
        """处理ping消息"""
        await websocket.send(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def notify_blogger(self, request_id: str, data: Dict[str, Any]):
        """通知博主有新的联系请求"""
        try:
            # 这里可以集成现有的邮件通知系统
            from lib.modules.notice_service import call_blogger
            
            message = f"""
新的联系请求 ({request_id}):

用户消息: {data.get('message', '无消息')}
用户代理: {data.get('userAgent', '未知')}
时间: {data.get('timestamp', '未知')}

请及时回复用户。
            """
            
            result = call_blogger(message=message.strip())
            logger.info(f"博主通知发送结果: {result}")
            
        except ImportError:
            logger.warning("邮件通知模块未找到，跳过邮件发送")
        except Exception as e:
            logger.error(f"发送博主通知时出错: {e}")
    
    async def generate_ai_response(self, message: str) -> str:
        """生成AI回复（占位实现）"""
        # 这里可以集成现有的AI问答系统
        if "你好" in message or "hello" in message.lower():
            return "您好！我是博客助手，有什么可以帮助您的吗？"
        elif "联系" in message or "客服" in message:
            return "已收到您的联系请求，博主将尽快回复您。"
        else:
            return "感谢您的消息！我会尽快处理您的请求。"
    
    async def start_server(self):
        """启动WebSocket服务器"""
        try:
            logger.info(f"启动WebSocket联系服务器在 {self.host}:{self.port}")
            
            async with websockets.serve(
                self.handle_contact_request, 
                self.host, 
                self.port,
                ping_interval=20,
                ping_timeout=10
            ):
                logger.info(f"WebSocket服务器已启动，监听 {self.host}:{self.port}")
                await asyncio.Future()  # 永久运行
                
        except Exception as e:
            logger.error(f"启动WebSocket服务器失败: {e}")
            raise

# 全局服务器实例
contact_server = ContactWebSocketServer()

async def start_contact_server():
    """启动联系服务器（异步入口点）"""
    await contact_server.start_server()

def run_contact_server():
    """运行联系服务器（同步入口点）"""
    asyncio.run(start_contact_server())

if __name__ == "__main__":
    # 直接运行服务器
    run_contact_server()

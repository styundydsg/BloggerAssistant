# ask.py - 集成WebSocket联系服务的FastAPI应用

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import json
import uuid
from datetime import datetime

# 添加lib目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib_dir = os.path.join(parent_dir, 'lib')
sys.path.append(lib_dir)

# 从新的模块化结构导入ask_question函数
# from deepseek_main import ask_question  # 在函数内部导入以避免循环导入

app = FastAPI(title="博客问答系统", description="集成WebSocket联系服务的问答API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议替换为具体域名，如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.contact_requests: dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # 发送连接确认
        await self.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket连接已建立",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }, client_id)

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))
    


# 创建全局连接管理器
manager = ConnectionManager()

# WebSocket联系端点 - 处理前端联系请求
@app.websocket("/contact")
async def websocket_contact_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
    
            message_data = json.loads(data)

            response = {
                "type": "message",
                "message": f"服务端收到你的消息: {message_data.get('message', '')}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(response))  
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"客户端 {client_id} 断开连接")
    except Exception as e:
        manager.disconnect(client_id)
        print(f"WebSocket连接处理错误: {e}")



# 添加一个简单的测试端点
@app.get("/test")
async def test():
    return {"message": "API is working"}

@app.post("/ask")
async def ask(request: Request):
    try:
        # 1. 尝试解析 JSON
        data = await request.json()
        
        # 2. 安全地获取 'question' 字段
        question = data.get('question')
        
        # 3. 明确检查 'question' 是否存在且不为空
        if not question:
            # 如果客户端没有提供 'question'，返回一个 400 Bad Request 错误
            # 这是客户端的错误，不是服务器的错误
            raise HTTPException(status_code=400, detail="No question provided in the request body.")
        
        # 4. 导入问答函数
        from deepseek_main import ask_question
        
        # 5. 调用你的 RAG 函数
        print(f"Calling ask_question with: {question}")  # 调试信息
        answer = ask_question(question)
        print(f"Received answer: {answer}")  # 调试信息
        
        # 6. 返回成功的响应
        return {"answer": answer}

    except HTTPException as http_exc:
        # 重新抛出我们主动引发的 HTTPException (比如 400 错误)
        raise http_exc
    except Exception as e:
        # 捕获所有其他未预料到的服务器内部错误 (比如 request.json() 解析失败)
        # 返回一个 500 Internal Server Error，并附上错误详情
        # 这对于调试非常有帮助！
        import traceback
        error_details = traceback.format_exc()
        print(f"Server error details: {error_details}")  # 在控制台输出详细错误信息
        return JSONResponse(
            status_code=500,
            content={"detail": f"An unexpected server error occurred: {str(e)}"}
        )

app = app

# 用于本地运行
if __name__ == "__main__":
    uvicorn.run("ask:app", host="127.0.0.1", port=8000, reload=True)

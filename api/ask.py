# ask.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

# 添加lib目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib_dir = os.path.join(parent_dir, 'lib')
sys.path.append(lib_dir)

# 从lib/deepseek_test.py导入ask_question函数
from deepseek_test import ask_question

app = FastAPI()

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
        
        # 4. 调用你的 RAG 函数
        print(f"Calling ask_question with: {question}")  # 调试信息
        answer = ask_question(question)
        print(f"Received answer: {answer}")  # 调试信息
        
        # 5. 返回成功的响应
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

# Vercel需要这个变量
app = app

# 用于本地运行
if __name__ == "__main__":
    uvicorn.run("ask:app", host="127.0.0.1", port=8000, reload=True)

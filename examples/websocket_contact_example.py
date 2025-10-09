"""WebSocket联系服务使用示例"""

import asyncio
import websockets
import json
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

async def example_contact_request():
    """示例：发送联系请求（模拟前端代码）"""
    print("=" * 60)
    print("WebSocket联系请求示例")
    print("=" * 60)
    
    try:
        # 连接WebSocket服务器

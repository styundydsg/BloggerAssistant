#!/usr/bin/env python3
"""测试API调用，模拟实际的问题提交"""

import requests
import json

def test_ask_endpoint():
    """测试/ask端点"""
    url = "http://127.0.0.1:8000/ask"
    
    # 测试数据
    test_data = {
        "question": "联系博主"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"回答: {result.get('answer')}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_ask_endpoint()

"""测试防轰炸机制"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor

# API基础URL（根据实际情况修改）
BASE_URL = "http://localhost:8000"  # 本地测试
# BASE_URL = "https://your-domain.vercel.app"  # 生产环境

def test_api_rate_limiting():
    """测试API速率限制"""
    print("=== 测试API速率限制 ===")
    
    # 测试正常请求
    print("1. 发送正常请求...")
    response = requests.post(f"{BASE_URL}/ask", json={"question": "你好，这是一个测试问题"})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    # 测试快速连续请求（模拟轰炸）
    print("2. 模拟快速连续请求（60次/分钟限制）...")
    success_count = 0
    limited_count = 0
    
    for i in range(70):  # 超过限制的请求次数
        response = requests.post(f"{BASE_URL}/ask", json={"question": f"测试问题 {i+1}"})
        
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            limited_count += 1
            if limited_count == 1:  # 只打印第一次被限制的信息
                print(f"第 {i+1} 次请求被限制: {response.json()}")
        
        # 稍微延迟以避免网络拥堵
        time.sleep(0.1)
    
    print(f"成功请求: {success_count}")
    print(f"被限制请求: {limited_count}")
    print()


def test_request_validation():
    """测试请求验证"""
    print("=== 测试请求验证 ===")
    
    # 测试空问题
    print("1. 测试空问题...")
    response = requests.post(f"{BASE_URL}/ask", json={"question": ""})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    # 测试超长问题
    print("2. 测试超长问题...")
    long_question = "a" * 1500  # 超过1000字符限制
    response = requests.post(f"{BASE_URL}/ask", json={"question": long_question})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    
    # 测试恶意内容
    print("3. 测试恶意内容检测...")
    malicious_questions = [
        "javascript:alert('xss')",
        "<script>alert('xss')</script>",
        "eval('malicious code')"
    ]
    
    for i, question in enumerate(malicious_questions, 1):
        response = requests.post(f"{BASE_URL}/ask", json={"question": question})
        print(f"恶意内容测试 {i}: 状态码 {response.status_code}")
        if response.status_code != 200:
            print(f"被阻止: {response.json()}")
    print()

def test_rate_limit_status():
    """测试速率限制状态查询"""
    print("=== 测试速率限制状态查询 ===")
    
    # 查询API限制状态
    response = requests.get(f"{BASE_URL}/contact/status")
    print("联系功能状态:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def stress_test():
    """压力测试（谨慎使用）"""
    print("=== 压力测试（谨慎使用）===")
    
    def make_request(i):
        try:
            response = requests.post(f"{BASE_URL}/ask", 
                                   json={"question": f"压力测试问题 {i}"},
                                   timeout=5)
            return response.status_code
        except:
            return "timeout"
    
    # 使用线程池模拟并发请求
    print("模拟10个并发请求...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(make_request, range(10)))
    
    status_counts = {}
    for result in results:
        status_counts[result] = status_counts.get(result, 0) + 1
    
    print("压力测试结果:")
    for status, count in status_counts.items():
        print(f"状态码 {status}: {count} 次")
    print()

if __name__ == "__main__":
    print("防轰炸机制测试开始")
    print("=" * 50)
    
    try:
        # 测试各项功能
        test_api_rate_limiting()
        test_request_validation()
        test_rate_limit_status()
        
        # 谨慎使用压力测试
        # stress_test()
        
        print("测试完成！")
        print("\n总结:")
        print("- API请求限制: 每分钟60次")
        print("- 邮件发送限制: 每小时5次") 
        print("- 内容安全检查: 长度限制和恶意内容检测")
        print("- 所有限制基于IP地址")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请确保API服务器正在运行")
        print(f"当前测试URL: {BASE_URL}")

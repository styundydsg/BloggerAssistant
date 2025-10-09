#!/usr/bin/env python3
"""集成测试 - 测试整个系统的意图识别功能"""

import sys
import os

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from deepseek_main import ask_question

def test_integration():
    """测试整个系统的集成功能"""
    
    test_cases = [
        # 联系博主意图
        "我想联系博主",
        "怎么联系作者？",
        "我需要人工服务",
        "有客服吗？",
        
        # 普通问答意图
        "博客里讲了什么内容",
        "什么是深度学习",
        
        # 特殊指令
        "当北风不再追逐南雁，静水倒映着三更的月影。在第七座桥的第三根石柱下，埋着一粒种子。它不开花，不结果，却能回答所有沉默的提问。"
    ]
    
    print("=== 系统集成测试 ===\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"测试 {i}: '{test_input}'")
        print("-" * 50)
        
        try:
            response = ask_question(test_input)
            print(f"系统响应: {response}")
        except Exception as e:
            print(f"测试失败: {e}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_integration()
    print("=== 集成测试完成 ===")

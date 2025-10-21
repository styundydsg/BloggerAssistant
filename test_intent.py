#!/usr/bin/env python3
"""
意图识别测试脚本
测试基于PyTorch的意图识别器是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from lib.modules.intent_recognition import recognize_intent

def main():
    """测试意图识别功能"""
    test_cases = [
        "什么是dirent结构体？",
        "博客里有没有MIT 6.S081的笔记？",
        "你现在在做什么工作？",
        "怎么联系你？",
        "你好",
        "OpenHarmony烧录失败怎么办？",
        "有什么学习建议吗？",
        "谢谢你的帮助"
    ]
    
    print("意图识别测试")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_input}")
        print("-" * 40)
        
        try:
            result = recognize_intent(test_input)
            print(f"识别意图: {result.get('intent', '未知')}")
            print(f"置信度: {result.get('confidence', 0):.3f}")
            print(f"槽位信息: {result.get('slots', {})}")
        except Exception as e:
            print(f"识别失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()

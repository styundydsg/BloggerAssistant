#!/usr/bin/env python3
"""测试意图识别功能"""

import sys
import os

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from modules.intent_recognition import recognize_intent, is_contact_intent, get_contact_response

def test_intent_recognition():
    """测试意图识别功能"""
    
    test_cases = [
        # 联系博主意图测试
        "我想联系博主",
        "怎么联系作者？",
        "我需要人工帮助",
        "有客服吗？",
        "email联系方式",
        "微信联系",
        "support needed",
        
        # 普通问答意图测试
        "博客里讲了什么内容",
        "什么是深度学习",
        "如何安装Python",
        "介绍一下机器学习",
        
        # 特殊指令测试
        "当北风不再追逐南雁",
        "特殊指令",
        "secret command"
    ]
    
    print("=== 意图识别功能测试 ===\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"测试 {i}: '{test_input}'")
        
        # 测试意图识别
        intent_result = recognize_intent(test_input)
        print(f"  意图: {intent_result.get('intent')}")
        print(f"  槽位: {intent_result.get('slots')}")
        print(f"  置信度: {intent_result.get('confidence')}")
        
        # 测试联系博主意图判断
        is_contact = is_contact_intent(test_input)
        print(f"  是否为联系博主意图: {is_contact}")
        
        # 如果是联系博主意图，测试响应生成
        if is_contact:
            response = get_contact_response(test_input)
            print(f"  联系博主响应: {response[:100]}...")
        
        print("-" * 50)

def test_contact_scenarios():
    """专门测试联系博主场景"""
    print("\n=== 联系博主场景专项测试 ===\n")
    
    contact_scenarios = [
        "我想联系博主",
        "怎么联系作者？",
        "我需要人工服务",
        "有客服吗？",
        "email联系方式",
        "微信联系",
        "support needed",
        "help me contact the author",
        "怎么找到博主的联系方式",
        "我想和博主交流"
    ]
    
    for scenario in contact_scenarios:
        print(f"输入: '{scenario}'")
        
        # 判断是否为联系博主意图
        is_contact = is_contact_intent(scenario)
        print(f"  识别结果: {'是联系博主意图' if is_contact else '不是联系博主意图'}")
        
        if is_contact:
            response = get_contact_response(scenario)
            print(f"  响应: {response}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_intent_recognition()
    test_contact_scenarios()
    
    print("\n=== 测试完成 ===")

#!/usr/bin/env python3
"""
简单意图识别测试脚本
测试意图识别功能是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from lib.modules.intent_recognition import recognize_intent, is_contact_intent, get_contact_response

def test_intent_recognition():
    """测试意图识别功能"""
    test_cases = [
        "怎么联系博主？",
        "有微信吗？",
        "邮箱是多少？",
        "什么是Python？",
        "博客里有什么内容？",
        "你好",
        "谢谢"
    ]
    
    print("意图识别功能测试")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_input}")
        print("-" * 40)
        
        try:
            # 测试意图识别
            result = recognize_intent(test_input)
            print(f"识别意图: {result.get('intent', '未知')}")
            print(f"置信度: {result.get('confidence', 0):.3f}")
            print(f"槽位信息: {result.get('slots', {})}")
            print(f"使用模型: {result.get('model_used', '未知')}")
            
            # 测试联系博主判断
            is_contact = is_contact_intent(test_input)
            print(f"是否为联系博主意图: {is_contact}")
            
            # 如果是联系博主意图，测试响应生成
            if is_contact:
                contact_response = get_contact_response(test_input)
                print(f"联系博主响应: {contact_response}")
                
        except Exception as e:
            print(f"识别失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_intent_recognition()

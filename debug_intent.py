#!/usr/bin/env python3
"""调试意图识别问题"""

import sys
import os

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from lib.modules.intent_recognition import recognize_intent, is_contact_intent, get_contact_response

def test_contact_intent():
    """测试联系博主意图识别"""
    test_input = "联系博主"
    
    print(f"测试输入: '{test_input}'")
    
    try:
        # 测试意图识别
        intent_result = recognize_intent(test_input)
        print(f"意图识别结果: {intent_result}")
        
        # 测试联系博主意图判断
        is_contact = is_contact_intent(test_input)
        print(f"是否为联系博主意图: {is_contact}")
        
        # 如果是联系博主意图，测试响应生成
        if is_contact:
            response = get_contact_response(test_input)
            print(f"联系博主响应: {response}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_contact_intent()

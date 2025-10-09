"""通知服务功能测试脚本"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from lib.modules.notification_service import (
    handle_user_session, 
    get_system_status, 
    manual_notify_users,
    cleanup_expired_users
)
from lib.modules.redis_manager import user_login, user_logout, get_online_users

def test_redis_connection():
    """测试Redis连接"""
    print("=" * 50)
    print("测试Redis连接")
    print("=" * 50)
    
    try:
        status = get_system_status()
        print(f"Redis连接状态: {'成功' if status['redis_connected'] else '失败'}")
        if not status['redis_connected']:
            print(f"错误信息: {status.get('error', '未知错误')}")
            return False
        print("✅ Redis连接测试通过")
        return True
    except Exception as e:
        print(f"❌ Redis连接测试失败: {e}")
        return False

def test_user_login_logout():
    """测试用户上线/下线功能"""
    print("\n" + "=" * 50)
    print("测试用户上线/下线功能")
    print("=" * 50)
    
    test_user_id = "test_user_001"
    user_info = {
        'username': '测试用户',
        'email': 'test@example.com',
        'ip_address': '127.0.0.1'
    }
    
    try:
        # 测试用户上线
        result = user_login(test_user_id, user_info)
        print(f"用户上线结果: {'成功' if result else '失败'}")
        
        # 检查在线状态
        online_users = get_online_users()
        print(f"当前在线用户: {online_users}")
        print(f"测试用户是否在线: {test_user_id in online_users}")
        
        # 测试用户下线
        result = user_logout(test_user_id)
        print(f"用户下线结果: {'成功' if result else '失败'}")
        
        # 再次检查在线状态
        online_users = get_online_users()
        print(f"下线后在线用户: {online_users}")
        print(f"测试用户是否在线: {test_user_id in online_users}")
        
        print("✅ 用户上线/下线测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 用户上线/下线测试失败: {e}")
        return False

def test_intent_recognition():
    """测试意图识别功能"""
    print("\n" + "=" * 50)
    print("测试意图识别功能")
    print("=" * 50)
    
    test_cases = [
        {
            'input': '我需要人工服务',
            'expected_intent': '联系博主',
            'description': '联系博主意图测试'
        },
        {
            'input': '博客里讲了什么内容',
            'expected_intent': '普通问答',
            'description': '普通问答意图测试'
        },
        {
            'input': '当北风不再追逐南雁',
            'expected_intent': '特殊指令',
            'description': '特殊指令意图测试'
        }
    ]
    
    test_user_id = "test_user_intent"
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['description']}")
            print(f"输入: {test_case['input']}")
            
            result = handle_user_session(test_user_id, test_case['input'])
            
            if result.get('error'):
                print(f"❌ 错误: {result['error']}")
                continue
            
            actual_intent = result.get('intent_details', {}).get('intent', '未知')
            confidence = result.get('intent_details', {}).get('confidence', 0)
            
            print(f"识别意图: {actual_intent}")
            print(f"置信度: {confidence:.2f}")
            print(f"是否发送通知: {result.get('notification_sent', False)}")
            
            if actual_intent == test_case['expected_intent']:
                print("✅ 意图识别正确")
            else:
                print(f"❌ 意图识别错误，期望: {test_case['expected_intent']}")
        
        print("✅ 意图识别测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 意图识别测试失败: {e}")
        return False

def test_notification_system():
    """测试通知系统功能"""
    print("\n" + "=" * 50)
    print("测试通知系统功能")
    print("=" * 50)
    
    # 创建几个测试用户
    test_users = [
        {'id': 'user_notify_001', 'info': {'username': '通知测试用户1'}},
        {'id': 'user_notify_002', 'info': {'username': '通知测试用户2'}},
        {'id': 'user_notify_003', 'info': {'username': '通知测试用户3'}}
    ]
    
    try:
        # 让测试用户上线
        for user in test_users:
            user_login(user['id'], user['info'])
            print(f"用户 {user['id']} 已上线")
        
        # 等待一下让通知服务启动
        time.sleep(2)
        
        # 测试手动通知
        test_message = "🚨 这是测试通知消息 🚨\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n发送测试通知: {test_message}")
        
        result = manual_notify_users(test_message, priority=1)
        print(f"通知结果: {result}")
        
        # 测试联系博主意图触发通知
        print("\n测试联系博主意图触发通知...")
        contact_result = handle_user_session('user_notify_001', '我需要人工客服帮助')
        print(f"联系博主意图处理结果: {contact_result.get('notification_result', {})}")
        
        # 等待通知发送完成
        time.sleep(3)
        
        # 检查系统状态
        status = get_system_status()
        print(f"\n系统状态:")
        print(f"- 在线用户数: {status['online_users_count']}")
        print(f"- 待处理通知: {status['pending_notifications']}")
        print(f"- 服务运行状态: {status['service_running']}")
        
        # 清理测试用户
        for user in test_users:
            user_logout(user['id'])
            print(f"用户 {user['id']} 已下线")
        
        print("✅ 通知系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 通知系统测试失败: {e}")
        return False

def test_cleanup_function():
    """测试清理功能"""
    print("\n" + "=" * 50)
    print("测试清理功能")
    print("=" * 50)
    
    try:
        # 执行清理
        cleanup_expired_users()
        print("✅ 清理功能测试完成")
        return True
    except Exception as e:
        print(f"❌ 清理功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("通知服务功能测试开始")
    print("=" * 60)
    
    # 执行所有测试
    tests = [
        ("Redis连接测试", test_redis_connection),
        ("用户上线/下线测试", test_user_login_logout),
        ("意图识别测试", test_intent_recognition),
        ("通知系统测试", test_notification_system),
        ("清理功能测试", test_cleanup_function)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 执行异常: {e}")
            results.append((test_name, False))
        
        print("\n" + "-" * 40 + "\n")
    
    # 输出测试总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！通知服务功能正常。")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查相关配置。")

if __name__ == "__main__":
    main()

"""通知服务使用示例"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from lib.modules.notification_service import (
    handle_user_session, 
    get_system_status, 
    manual_notify_users
)
from lib.modules.redis_manager import user_login, user_logout, get_online_users

def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("基础使用示例")
    print("=" * 60)
    
    # 1. 检查系统状态
    print("1. 检查系统状态:")
    status = get_system_status()
    print(f"   - Redis连接: {'✅ 正常' if status['redis_connected'] else '❌ 异常'}")
    print(f"   - 在线用户数: {status['online_users_count']}")
    print(f"   - 服务状态: {'✅ 运行中' if status['service_running'] else '❌ 停止'}")
    
    # 2. 用户上线示例
    print("\n2. 用户上线示例:")
    user_id = "example_user_001"
    user_info = {
        'username': '示例用户',
        'email': 'user@example.com',
        'ip_address': '192.168.1.100',
        'browser': 'Chrome'
    }
    
    if user_login(user_id, user_info):
        print(f"   ✅ 用户 {user_id} 上线成功")
    else:
        print(f"   ❌ 用户 {user_id} 上线失败")
    
    # 3. 处理用户会话（普通问答）
    print("\n3. 处理普通问答会话:")
    result = handle_user_session(user_id, "博客里讲了什么内容？")
    print(f"   - 意图识别: {result.get('intent_details', {}).get('intent', '未知')}")
    print(f"   - 是否发送通知: {'是' if result.get('notification_sent') else '否'}")
    
    # 4. 处理用户会话（联系博主意图）
    print("\n4. 处理联系博主会话:")
    result = handle_user_session(user_id, "我需要人工客服帮助")
    print(f"   - 意图识别: {result.get('intent_details', {}).get('intent', '未知')}")
    print(f"   - 是否发送通知: {'是' if result.get('notification_sent') else '否'}")
    
    if result.get('notification_sent'):
        notification_result = result.get('notification_result', {})
        print(f"   - 通知用户数: {notification_result.get('total_users', 0)}")
        print(f"   - 成功通知: {len(notification_result.get('notified_users', []))}")
    
    # 5. 手动发送通知
    print("\n5. 手动发送通知示例:")
    message = "📢 系统维护通知\n系统将于今晚进行维护，预计耗时1小时。"
    result = manual_notify_users(message, priority=1)
    print(f"   - 通知结果: {result}")
    
    # 6. 用户下线
    print("\n6. 用户下线:")
    if user_logout(user_id):
        print(f"   ✅ 用户 {user_id} 下线成功")
    else:
        print(f"   ❌ 用户 {user_id} 下线失败")
    
    print("\n✅ 基础使用示例完成")

def example_multiple_users():
    """多用户场景示例"""
    print("\n" + "=" * 60)
    print("多用户场景示例")
    print("=" * 60)
    
    # 创建多个测试用户
    users = [
        {'id': 'multi_user_001', 'name': '用户A'},
        {'id': 'multi_user_002', 'name': '用户B'}, 
        {'id': 'multi_user_003', 'name': '用户C'}
    ]
    
    # 所有用户上线
    print("1. 多用户上线:")
    for user in users:
        user_info = {'username': user['name']}
        if user_login(user['id'], user_info):
            print(f"   ✅ {user['name']} 上线成功")
        else:
            print(f"   ❌ {user['name']} 上线失败")
    
    # 检查在线用户
    online_users = get_online_users()
    print(f"\n2. 当前在线用户: {online_users}")
    
    # 模拟用户活动
    print("\n3. 模拟用户活动:")
    activities = [
        ('multi_user_001', '我想了解博客的技术细节'),
        ('multi_user_002', '我需要人工技术支持'),
        ('multi_user_003', '博客的更新频率是多少？')
    ]
    
    for user_id, user_input in activities:
        print(f"   👤 {user_id}: {user_input}")
        result = handle_user_session(user_id, user_input)
        intent = result.get('intent_details', {}).get('intent', '未知')
        notified = result.get('notification_sent', False)
        print(f"     意图: {intent}, 通知: {'✅ 已发送' if notified else '❌ 未发送'}")
    
    # 发送广播通知
    print("\n4. 发送广播通知:")
    broadcast_msg = "🎉 欢迎所有在线用户！系统运行正常。"
    result = manual_notify_users(broadcast_msg, priority=1)
    print(f"   - 通知用户数: {result.get('total_users', 0)}")
    print(f"   - 成功通知: {len(result.get('notified_users', []))}")
    
    # 所有用户下线
    print("\n5. 多用户下线:")
    for user in users:
        if user_logout(user['id']):
            print(f"   ✅ {user['name']} 下线成功")
        else:
            print(f"   ❌ {user['name']} 下线失败")
    
    print("\n✅ 多用户场景示例完成")

def example_priority_notifications():
    """优先级通知示例"""
    print("\n" + "=" * 60)
    print("优先级通知示例")
    print("=" * 60)
    
    # 创建测试用户
    user_id = "priority_user"
    user_login(user_id, {'username': '优先级测试用户'})
    
    # 发送不同优先级的通知
    notifications = [
        ("低优先级通知 - 一般消息", 1),
        ("中优先级通知 - 重要更新", 2), 
        ("高优先级通知 - 紧急维护", 3),
        ("联系博主意图触发的高优先级通知", 2)  # 联系博主意图默认优先级为2
    ]
    
    print("1. 发送不同优先级的通知:")
    for message, priority in notifications:
        if "联系博主" in message:
            # 通过意图识别触发通知
            result = handle_user_session(user_id, "我需要紧急人工帮助")
            print(f"   🔔 优先级{priority}: {message}")
            print(f"      意图触发通知: {result.get('notification_sent', False)}")
        else:
            # 手动发送通知
            result = manual_notify_users(message, priority)
            print(f"   🔔 优先级{priority}: {message}")
            print(f"      通知结果: {len(result.get('notified_users', []))}个用户")
    
    # 等待通知处理
    time.sleep(2)
    
    # 检查系统状态
    status = get_system_status()
    print(f"\n2. 系统状态:")
    print(f"   - 在线用户: {status['online_users_count']}")
    print(f"   - 待处理通知: {status['pending_notifications']}")
    
    # 用户下线
    user_logout(user_id)
    print("\n✅ 优先级通知示例完成")

def example_integration_with_web_app():
    """Web应用集成示例"""
    print("\n" + "=" * 60)
    print("Web应用集成示例")
    print("=" * 60)
    
    print("""
在实际Web应用中，可以这样集成通知服务：

1. 用户访问时自动上线:
```python
# 在用户会话开始时
user_id = session.get('user_id')  # 或从JWT token获取
user_info = {
    'username': current_user.username,
    'ip_address': request.remote_addr,
    'user_agent': request.headers.get('User-Agent')
}
user_login(user_id, user_info)
```

2. 处理用户消息时检查意图:
```python
def handle_user_message(user_id, message):
    result = handle_user_session(user_id, message)
    
    if result.get('contact_intent'):
        # 联系博主意图，记录到数据库或发送邮件
        log_contact_request(user_id, message, result)
        
    # 返回适当的响应
    if result.get('intent_details', {}).get('intent') == '联系博主':
        return "已收到您的联系请求，博主将尽快回复您。"
    else:
        return generate_ai_response(message)
```

3. 定期清理过期用户:
```python
# 在定时任务中
@app.route('/admin/cleanup')
def cleanup_expired_users():
    cleanup_expired_users()
    return "过期用户清理完成"
```

4. 管理员发送通知:
```python
@app.route('/admin/notify', methods=['POST'])
def admin_notify():
    message = request.json.get('message')
    priority = request.json.get('priority', 1)
    result = manual_notify_users(message, priority)
    return jsonify(result)
```
""")
    
    print("✅ Web应用集成示例完成")

def main():
    """主函数 - 运行所有示例"""
    print("通知服务使用示例")
    print("=" * 80)
    
    examples = [
        ("基础使用示例", example_basic_usage),
        ("多用户场景示例", example_multiple_users),
        ("优先级通知示例", example_priority_notifications),
        ("Web应用集成示例", example_integration_with_web_app)
    ]
    
    for example_name, example_func in examples:
        try:
            example_func()
            print("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"❌ {example_name} 执行失败: {e}")
            print("\n" + "=" * 80 + "\n")
    
    print("🎉 所有示例执行完成！")
    print("\n使用提示:")
    print("1. 确保Redis服务正在运行 (localhost:6380, 密码:123456)")
    print("2. 确保DeepSeek API密钥已配置")
    print("3. 通知服务会自动启动后台线程处理通知队列")
    print("4. 用户信息会在24小时后自动过期")

if __name__ == "__main__":
    main()

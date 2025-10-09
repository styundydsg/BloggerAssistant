"""Redis使用示例 - 展示如何在项目中使用Redis功能"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.modules.redis_manager import get_redis_manager

def example_basic_usage():
    """基本使用示例"""
    print("=" * 50)
    print("Redis基本使用示例")
    print("=" * 50)
    
    # 获取Redis管理器
    redis_manager = get_redis_manager()
    
    # 缓存数据示例
    cache_key = "cache:user:profile:1001"
    user_profile = {
        "name": "李四",
        "age": 25,
        "email": "lisi@example.com",
        "last_login": "2024-09-24 11:30:00"
    }
    
    # 设置缓存（过期时间1小时）
    if redis_manager.set_value(cache_key, str(user_profile), expire=3600):
        print("✅ 用户资料缓存设置成功")
    
    # 获取缓存
    cached_profile = redis_manager.get_value(cache_key)
    if cached_profile:
        print("✅ 从缓存获取用户资料成功")
        print(f"缓存内容: {cached_profile}")
    
    # 会话管理示例
    session_key = "session:user:2001"
    session_data = {
        "user_id": 2001,
        "username": "wangwu",
        "permissions": ["read", "write"],
        "login_time": time.time()
    }
    
    # 设置会话（过期时间30分钟）
    if redis_manager.set_hash(session_key, session_data):
        print("✅ 用户会话设置成功")
    
    # 获取会话
    session_info = redis_manager.get_hash(session_key)
    if session_info:
        print("✅ 获取用户会话成功")
        print(f"会话信息: {session_info}")
    
    # 消息队列示例
    message_queue = "queue:messages"
    messages = [
        "系统通知: 服务器将在今晚维护",
        "用户消息: 你好，欢迎使用我们的服务",
        "系统警告: 磁盘空间不足"
    ]
    
    # 添加消息到队列
    for message in messages:
        if redis_manager.push_list(message_queue, message):
            print(f"✅ 消息添加到队列: {message}")
    
    # 读取队列消息
    queued_messages = redis_manager.get_list(message_queue)
    if queued_messages:
        print("✅ 从队列读取消息成功")
        for i, msg in enumerate(queued_messages, 1):
            print(f"消息 {i}: {msg}")
    
    # 计数器示例
    counter_key = "counter:page:views:home"
    
    # 增加计数器
    for i in range(5):
        # 模拟页面访问
        current_count = redis_manager.get_value(counter_key)
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        new_count = current_count + 1
        redis_manager.set_value(counter_key, str(new_count))
        print(f"✅ 页面访问计数: {new_count}")
        time.sleep(0.5)  # 模拟间隔

def example_advanced_features():
    """高级功能示例"""
    print("\n" + "=" * 50)
    print("Redis高级功能示例")
    print("=" * 50)
    
    redis_manager = get_redis_manager()
    
    # 连接状态检查
    if redis_manager.is_connected():
        print("✅ Redis连接正常")
        
        # 获取服务器信息
        info = redis_manager.get_info()
        if info:
            print("Redis服务器信息:")
            print(f"  - 版本: {info.get('redis_version', '未知')}")
            print(f"  - 运行时间: {info.get('uptime_in_seconds', '未知')}秒")
            print(f"  - 内存使用: {info.get('used_memory_human', '未知')}")
            print(f"  - 连接客户端: {info.get('connected_clients', '未知')}")
    else:
        print("❌ Redis连接异常")
    
    # 批量操作示例
    print("\n批量操作示例:")
    keys_to_set = {
        "batch:key1": "value1",
        "batch:key2": "value2", 
        "batch:key3": "value3"
    }
    
    for key, value in keys_to_set.items():
        if redis_manager.set_value(key, value):
            print(f"✅ 设置 {key} = {value}")
    
    # 检查多个键是否存在
    keys_to_check = ["batch:key1", "batch:key2", "nonexistent:key"]
    for key in keys_to_check:
        exists = redis_manager.exists(key)
        status = "存在" if exists else "不存在"
        print(f"键 {key}: {status}")

def main():
    """主函数"""
    print("Redis功能使用示例")
    print("=" * 50)
    
    # 检查Redis连接
    redis_manager = get_redis_manager()
    if not redis_manager.connect():
        print("❌ 无法连接到Redis服务器")
        print("请确保Redis服务器正在运行")
        print("默认配置: localhost:6380, 密码: 123456")
        return
    
    # 运行示例
    example_basic_usage()
    example_advanced_features()
    
    # 清理测试数据
    print("\n" + "=" * 50)
    print("清理测试数据")
    print("=" * 50)
    
    test_keys = [
        "cache:user:profile:1001",
        "session:user:2001", 
        "queue:messages",
        "counter:page:views:home",
        "batch:key1",
        "batch:key2",
        "batch:key3"
    ]
    
    for key in test_keys:
        if redis_manager.delete_key(key):
            print(f"✅ 清理键: {key}")
    
    # 断开连接
    redis_manager.disconnect()
    print("\n🎉 Redis功能示例完成")

if __name__ == "__main__":
    main()

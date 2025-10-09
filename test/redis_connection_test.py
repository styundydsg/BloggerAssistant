"""Redis连接测试脚本 - 测试Redis连接和基本操作功能"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.modules.redis_manager import RedisManager, test_redis_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_operations():
    """测试基本Redis操作"""
    print("=" * 50)
    print("开始测试Redis基本操作")
    print("=" * 50)
    
    # 创建Redis管理器
    manager = RedisManager()
    
    # 测试连接
    if not manager.connect():
        print("❌ Redis连接失败")
        return False
    
    print("✅ Redis连接成功")
    
    # 测试键值对操作
    test_key = "test:key"
    test_value = "Hello Redis!"
    
    # 设置值
    if manager.set_value(test_key, test_value):
        print("✅ 设置键值对成功")
    else:
        print("❌ 设置键值对失败")
        return False
    
    # 获取值
    retrieved_value = manager.get_value(test_key)
    if retrieved_value == test_value:
        print("✅ 获取键值对成功")
    else:
        print("❌ 获取键值对失败")
        return False
    
    # 测试过期时间
    expire_key = "test:expire_key"
    expire_value = "This will expire in 5 seconds"
    
    if manager.set_value(expire_key, expire_value, expire=5):
        print("✅ 设置带过期时间的键值对成功")
    else:
        print("❌ 设置带过期时间的键值对失败")
        return False
    
    # 检查键是否存在
    if manager.exists(test_key):
        print("✅ 检查键存在性成功")
    else:
        print("❌ 检查键存在性失败")
        return False
    
    # 测试哈希表操作
    hash_name = "test:user:1"
    user_data = {
        "name": "张三",
        "age": "30",
        "email": "zhangsan@example.com"
    }
    
    if manager.set_hash(hash_name, user_data):
        print("✅ 设置哈希表成功")
    else:
        print("❌ 设置哈希表失败")
        return False
    
    # 获取哈希表
    retrieved_user = manager.get_hash(hash_name)
    if retrieved_user == user_data:
        print("✅ 获取哈希表成功")
    else:
        print("❌ 获取哈希表失败")
        return False
    
    # 测试列表操作
    list_name = "test:messages"
    messages = ["消息1", "消息2", "消息3"]
    
    if manager.push_list(list_name, *messages):
        print("✅ 向列表添加元素成功")
    else:
        print("❌ 向列表添加元素失败")
        return False
    
    # 获取列表
    retrieved_messages = manager.get_list(list_name)
    if retrieved_messages == messages:
        print("✅ 获取列表元素成功")
    else:
        print("❌ 获取列表元素失败")
        return False
    
    # 测试删除操作
    if manager.delete_key(test_key):
        print("✅ 删除键成功")
    else:
        print("❌ 删除键失败")
        return False
    
    # 验证键已被删除
    if not manager.exists(test_key):
        print("✅ 验证键删除成功")
    else:
        print("❌ 验证键删除失败")
        return False
    
    # 获取服务器信息
    info = manager.get_info()
    if info:
        print("✅ 获取服务器信息成功")
        print(f"Redis版本: {info.get('redis_version', '未知')}")
        print(f"已连接客户端数: {info.get('connected_clients', '未知')}")
        print(f"已使用内存: {info.get('used_memory_human', '未知')}")
    else:
        print("❌ 获取服务器信息失败")
        return False
    
    # 断开连接
    manager.disconnect()
    print("✅ Redis连接已关闭")
    
    return True

def test_connection_function():
    """测试连接函数"""
    print("\n" + "=" * 50)
    print("测试连接函数")
    print("=" * 50)
    
    if test_redis_connection():
        print("✅ 连接函数测试成功")
        return True
    else:
        print("❌ 连接函数测试失败")
        return False

def main():
    """主测试函数"""
    print("Redis连接功能测试")
    print("=" * 50)
    
    # 测试连接函数
    if not test_connection_function():
        print("\n⚠️ 连接测试失败，请检查Redis服务器是否运行")
        print("请确保Redis服务器运行在 localhost:6380")
        print("或通过环境变量设置正确的连接参数:")
        print("  - REDIS_HOST: Redis服务器地址")
        print("  - REDIS_PORT: Redis服务器端口")
        print("  - REDIS_PASSWORD: Redis密码")
        print("  - REDIS_DB: Redis数据库编号")
        return
    
    # 测试基本操作
    if test_basic_operations():
        print("\n🎉 所有测试通过！Redis功能正常")
    else:
        print("\n💥 部分测试失败，请检查Redis配置和连接")

if __name__ == "__main__":
    main()

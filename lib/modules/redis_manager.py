"""Redis管理模块 - 提供Redis连接和操作功能"""

import redis
from .config import CONFIG
import logging
from typing import Any, Optional, Union, List, Dict

# 设置日志
logger = logging.getLogger(__name__)

class RedisManager:
    """Redis连接管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化Redis管理器
        
        Args:
            config: Redis配置字典，如果为None则使用默认配置
        """
        self.config = config or CONFIG.get("REDIS_CONFIG", {})
        self._client = None
        self._is_connected = False
    
    def connect(self) -> bool:
        """
        连接到Redis服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self._client = redis.Redis(
                host=self.config.get("HOST", "localhost"),
                port=self.config.get("PORT", 6380),
                db=self.config.get("DB", 0),
                password=self.config.get("PASSWORD"),
                decode_responses=self.config.get("DECODE_RESPONSES", True),
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            if self._client.ping():
                self._is_connected = True
                logger.info("成功连接到Redis服务器")
                return True
            else:
                logger.error("Redis连接测试失败")
                return False
                
        except redis.exceptions.ConnectionError as e:
            logger.error(f"无法连接到Redis服务器: {e}")
            return False
        except Exception as e:
            logger.error(f"Redis连接异常: {e}")
            return False
    
    def disconnect(self):
        """断开Redis连接"""
        if self._client:
            try:
                self._client.close()
                self._is_connected = False
                logger.info("Redis连接已关闭")
            except Exception as e:
                logger.error(f"关闭Redis连接时出错: {e}")
    
    def is_connected(self) -> bool:
        """检查是否已连接到Redis"""
        if not self._is_connected or not self._client:
            return False
        
        try:
            return self._client.ping()
        except:
            self._is_connected = False
            return False
    
    def set_value(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值
            expire: 过期时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            if expire:
                self._client.setex(key, expire, value)
            else:
                self._client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"设置Redis键值对失败: {e}")
            return False
    
    def get_value(self, key: str) -> Optional[Any]:
        """
        获取键值
        
        Args:
            key: 键名
            
        Returns:
            Optional[Any]: 键值，如果键不存在则返回None
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"获取Redis键值失败: {e}")
            return None
    
    def delete_key(self, key: str) -> bool:
        """
        删除键
        
        Args:
            key: 键名
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            result = self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"删除Redis键失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键是否存在
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"检查Redis键存在性失败: {e}")
            return False
    
    def set_hash(self, name: str, mapping: Dict[str, Any]) -> bool:
        """
        设置哈希表
        
        Args:
            name: 哈希表名
            mapping: 键值对字典
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            self._client.hset(name, mapping=mapping)
            return True
        except Exception as e:
            logger.error(f"设置Redis哈希表失败: {e}")
            return False
    
    def get_hash(self, name: str, key: Optional[str] = None) -> Union[Dict[str, Any], Optional[Any]]:
        """
        获取哈希表值
        
        Args:
            name: 哈希表名
            key: 哈希键名，如果为None则返回整个哈希表
            
        Returns:
            Union[Dict[str, Any], Optional[Any]]: 哈希表或单个值
        """
        if not self.is_connected():
            if not self.connect():
                return {} if key is None else None
        
        try:
            if key is None:
                return self._client.hgetall(name)
            else:
                return self._client.hget(name, key)
        except Exception as e:
            logger.error(f"获取Redis哈希表失败: {e}")
            return {} if key is None else None
    
    def push_list(self, name: str, *values: Any) -> bool:
        """
        向列表添加元素
        
        Args:
            name: 列表名
            *values: 要添加的值
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            self._client.rpush(name, *values)
            return True
        except Exception as e:
            logger.error(f"向Redis列表添加元素失败: {e}")
            return False
    
    def get_list(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表元素
        
        Args:
            name: 列表名
            start: 起始索引
            end: 结束索引
            
        Returns:
            List[Any]: 列表元素
        """
        if not self.is_connected():
            if not self.connect():
                return []
        
        try:
            return self._client.lrange(name, start, end)
        except Exception as e:
            logger.error(f"获取Redis列表失败: {e}")
            return []
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取Redis服务器信息
        
        Returns:
            Dict[str, Any]: 服务器信息
        """
        if not self.is_connected():
            if not self.connect():
                return {}
        
        try:
            return self._client.info()
        except Exception as e:
            logger.error(f"获取Redis服务器信息失败: {e}")
            return {}


# 创建全局Redis管理器实例
redis_manager = RedisManager()


def get_redis_manager() -> RedisManager:
    """
    获取Redis管理器实例
    
    Returns:
        RedisManager: Redis管理器实例
    """
    return redis_manager


def test_redis_connection() -> bool:
    """
    测试Redis连接
    
    Returns:
        bool: 连接是否成功
    """
    manager = RedisManager()
    return manager.connect()

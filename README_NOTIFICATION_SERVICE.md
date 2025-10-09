# Redis通知服务

这是一个基于Redis的在线状态管理和顺序通知系统，集成了意图识别功能，能够自动检测用户是否需要人工介入并发送通知。

## 功能特性

- ✅ **用户状态管理**: 自动记录用户上线/下线状态
- ✅ **意图识别**: 使用AI识别用户是否需要人工介入
- ✅ **顺序通知**: 按优先级顺序发送通知给在线用户
- ✅ **自动清理**: 24小时自动清理过期用户
- ✅ **后台服务**: 自动运行的通知处理线程
- ✅ **系统监控**: 实时查看系统状态和在线用户
- ✅ **邮件通知**: 通过QQ邮箱发送联系通知

## 系统架构

```
用户会话 → 意图识别 → 联系博主意图 → 通知服务 → Redis队列 → 顺序发送 → 在线用户
```

## 快速开始

### 1. 环境要求

- Python 3.7+
- Redis服务器 (localhost:6380, 密码:123456)
- DeepSeek API密钥

### 2. 安装依赖

```bash
pip install redis openai
```

### 3. 基本使用

```python
from lib.modules.notification_service import handle_user_session, get_system_status

# 处理用户会话（自动上线、意图识别、通知）
result = handle_user_session(
    user_id="user_001",
    user_input="我需要人工客服帮助",
    user_info={"username": "测试用户", "email": "test@example.com"}
)

print(f"意图: {result['intent_details']['intent']}")
print(f"是否发送通知: {result['notification_sent']}")

# 查看系统状态
status = get_system_status()
print(f"在线用户数: {status['online_users_count']}")
```

### 4. 核心功能

#### 用户管理
```python
from lib.modules.redis_manager import user_login, user_logout, get_online_users

# 用户上线
user_login("user_001", {"username": "张三", "ip_address": "192.168.1.100"})

# 用户下线
user_logout("user_001")

# 获取在线用户
online_users = get_online_users()
```

#### 通知功能
```python
from lib.modules.notification_service import manual_notify_users

# 手动发送通知
result = manual_notify_users("系统维护通知", priority=2)
print(f"成功通知: {len(result['notified_users'])}个用户")
```

#### 系统监控
```python
from lib.modules.notification_service import get_system_status, cleanup_expired_users

# 获取系统状态
status = get_system_status()
print(f"Redis连接: {status['redis_connected']}")
print(f"服务运行: {status['service_running']}")

# 清理过期用户
cleanup_expired_users()
```

## 集成示例

### Web应用集成

```python
from flask import Flask, request, jsonify
from lib.modules.notification_service import handle_user_session

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_id = request.json.get('user_id')
    message = request.json.get('message')
    
    # 处理用户消息
    result = handle_user_session(user_id, message)
    
    if result.get('contact_intent'):
        # 联系博主意图，记录到数据库
        log_contact_request(user_id, message, result)
        return jsonify({
            "response": "已收到您的联系请求，博主将尽快回复您。",
            "contact_request": True
        })
    else:
        # 普通问答，返回AI响应
        ai_response = generate_ai_response(message)
        return jsonify({"response": ai_response})

@app.route('/admin/status')
def admin_status():
    status = get_system_status()
    return jsonify(status)
```

### 定时任务集成

```python
import schedule
import time
from lib.modules.notification_service import cleanup_expired_users

# 每小时清理一次过期用户
schedule.every().hour.do(cleanup_expired_users)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## API参考

### NotificationService类

#### handle_user_session(user_id, user_input, user_info=None)
处理用户会话，包括上线、意图识别和通知。

**参数:**
- `user_id`: 用户唯一标识
- `user_input`: 用户输入文本
- `user_info`: 可选用户信息字典

**返回:**
```python
{
    'user_id': 'user_001',
    'intent_recognized': True,
    'contact_intent': True,
    'notification_sent': True,
    'intent_details': {
        'intent': '联系博主',
        'confidence': 0.95,
        'slots': {'contact_method': '人工服务'}
    },
    'notification_result': {
        'total_users': 3,
        'notified_users': ['user_001', 'user_002'],
        'failed_users': []
    }
}
```

#### get_system_status()
获取系统状态信息。

**返回:**
```python
{
    'redis_connected': True,
    'online_users_count': 3,
    'online_users': ['user_001', 'user_002', 'user_003'],
    'pending_notifications': 0,
    'service_running': True,
    'last_update': '2025-09-23 23:07:49'
}
```

### RedisManager类

#### user_login(user_id, user_info=None)
用户上线，标记为在线状态。

#### user_logout(user_id)
用户下线，移除在线状态。

#### notify_online_users(message, priority=1)
通知所有在线用户。

#### get_online_users()
获取所有在线用户ID。

## 配置说明

### Redis配置
默认配置:
- 主机: localhost
- 端口: 6380
- 数据库: 0
- 密码: 123456

修改配置:
```python
from lib.modules.redis_manager import RedisManager

manager = RedisManager(
    host='your-redis-host',
    port=6379,
    password='your-password'
)
```

### 意图识别配置
系统使用DeepSeek API进行意图识别，需要在环境变量中设置:
```bash
export DEEPSEEK_API_KEY=your-api-key
```

### 邮件配置
系统支持通过QQ邮箱发送联系通知，需要在环境变量中设置:
```bash
export SENDER_EMAIL=your_email@qq.com
export SENDER_PASSWORD=your_authorization_code
export RECIPIENT_EMAIL=recipient@qq.com
```

**获取QQ邮箱授权码:**
1. 登录QQ邮箱网页版
2. 进入"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"POP3/SMTP服务"
5. 按照提示获取授权码（不是邮箱密码）

**邮件发送功能:**
```python
from lib.modules.notice_service import call_blogger

# 发送默认联系邮件
result = call_blogger()
print(result)

# 自定义邮件内容
custom_message = """
尊敬的博主：

我是您的读者，对您的文章很感兴趣。
希望与您进一步交流。

谢谢！
"""
result = call_blogger(message=custom_message)
print(result)

# 发送到特定邮箱
result = call_blogger(
    message="测试邮件", 
    recipient_email="specific@qq.com"
)
print(result)
```

## 测试

运行完整测试套件:
```bash
python test/notification_service_test.py
```

运行使用示例:
```bash
python examples/notification_service_example.py
```

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务是否运行
   - 验证主机、端口、密码配置

2. **意图识别失败**
   - 检查DeepSeek API密钥配置
   - 验证网络连接

3. **通知发送失败**
   - 检查在线用户是否存在
   - 查看Redis数据结构是否正确

### 日志查看

系统使用Python标准logging模块，日志级别为INFO，可以查看详细的操作日志。

## 扩展开发

### 添加新的通知渠道

重写`_send_notification_to_user`方法:
```python
def _send_notification_to_user(self, user_id: str, message: str) -> bool:
    # 发送邮件
    send_email(user_id, message)
    
    # 发送短信
    send_sms(user_id, message)
    
    # WebSocket推送
    websocket_push(user_id, message)
    
    return True
```

### 自定义意图识别

修改意图识别模板或添加新的意图类型。

## 许可证

MIT License

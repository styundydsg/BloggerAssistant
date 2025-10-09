# QQ邮箱SMTP配置指南

## 环境变量配置

在使用邮件发送功能前，需要设置以下环境变量：

### Windows系统
```cmd
set SENDER_EMAIL=your_email@qq.com
set SENDER_PASSWORD=your_authorization_code
set RECIPIENT_EMAIL=recipient@qq.com
```

### Linux/Mac系统
```bash
export SENDER_EMAIL="your_email@qq.com"
export SENDER_PASSWORD="your_authorization_code"
export RECIPIENT_EMAIL="recipient@qq.com"
```

### 在Python代码中设置
```python
import os
os.environ["SENDER_EMAIL"] = "your_email@qq.com"
os.environ["SENDER_PASSWORD"] = "your_authorization_code"
os.environ["RECIPIENT_EMAIL"] = "recipient@qq.com"
```

## 获取QQ邮箱授权码

1. 登录QQ邮箱网页版
2. 进入"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"POP3/SMTP服务"
5. 按照提示获取授权码（不是邮箱密码）

## 配置说明

- **SENDER_EMAIL**: 发件人QQ邮箱地址
- **SENDER_PASSWORD**: QQ邮箱授权码（16位字符）
- **RECIPIENT_EMAIL**: 收件人邮箱地址（可以是任何邮箱）
- **SMTP_SERVER**: smtp.qq.com（默认）
- **SMTP_PORT**: 587（默认，使用TLS加密）

## 使用示例

### 基本使用
```python
from modules.notice_service import call_blogger

# 发送默认联系邮件
result = call_blogger()
print(result)
```

### 自定义邮件内容
```python
from modules.notice_service import call_blogger

custom_message = """
尊敬的博主：

我是您的读者，对您的文章很感兴趣。
希望与您进一步交流。

谢谢！
"""

result = call_blogger(message=custom_message)
print(result)
```

### 发送到特定邮箱
```python
from modules.notice_service import call_blogger

result = call_blogger(
    message="测试邮件", 
    recipient_email="specific@qq.com"
)
print(result)
```

## 错误处理

函数会返回详细的错误信息，包括：
- 配置缺失错误
- SMTP认证失败
- 网络连接问题
- 其他异常情况

## 安全建议

1. 不要将授权码硬编码在代码中
2. 使用环境变量或配置文件管理敏感信息
3. 定期更换授权码
4. 在生产环境中使用安全的配置管理方式

# 防轰炸机制配置指南

## 概述

本文档介绍如何在您的代码中防止被轰炸攻击。防轰炸机制通过速率限制、请求验证和内容安全检查来保护您的API和邮件服务。

## 已实现的功能

### 1. 速率限制 (Rate Limiting)

基于Redis的分布式速率限制，支持多种操作类型：

- **API请求**: 每分钟60次
- **邮件发送**: 每小时5次  
- **联系功能**: 每小时5次
- **通用限制**: 每分钟100次

### 2. 请求验证 (Request Validation)

- **长度检查**: 问题不超过1000字符，消息不超过5000字符
- **内容安全**: 检测恶意脚本和危险内容
- **空值检查**: 防止空请求

### 3. IP地址追踪

所有限制基于客户端IP地址，防止单个用户滥用服务。

## 使用方法

### 在API端点中使用

```python
from lib.modules.rate_limiter import get_request_validator

@app.post("/your-endpoint")
async def your_endpoint(request: Request):
    # 验证请求
    validator = get_request_validator()
    is_valid, error_msg = validator.validate_api_request(request, user_input)
    
    if not is_valid:
        raise HTTPException(status_code=429, detail=error_msg)
    
    # 处理正常请求
    return {"result": "success"}
```

### 自定义限制配置

```python
from lib.modules.rate_limiter import get_rate_limiter

# 自定义限制
custom_limits = {
    "requests": 30,    # 30次请求
    "window": 300      # 5分钟窗口
}

rate_limiter = get_rate_limiter()
is_limited, info = rate_limiter.is_rate_limited(
    "user_id_123", 
    "custom_action", 
    custom_limits
)
```

## 配置文件

### 默认限制配置

在 `lib/modules/rate_limiter.py` 中修改默认限制：

```python
self.default_limits = {
    "api": {"requests": 60, "window": 60},      # 每分钟60次
    "email": {"requests": 10, "window": 3600},  # 每小时10次
    "contact": {"requests": 5, "window": 3600}, # 每小时5次
    "general": {"requests": 100, "window": 60}  # 每分钟100次
}
```

### 环境变量配置

可以通过环境变量动态调整限制：

```bash
# 设置API限制
export API_RATE_LIMIT=30
export API_WINDOW_SIZE=60

# 设置邮件限制  
export EMAIL_RATE_LIMIT=5
export EMAIL_WINDOW_SIZE=3600
```

## 监控和调试

### 查看限制状态

```python
from lib.modules.rate_limiter import get_rate_limiter

rate_limiter = get_rate_limiter()
status = rate_limiter.get_rate_limit_info("user_ip", "api")
print(status)
```

### API状态端点

已实现的API端点：
- `GET /contact/status` - 查看联系功能限制状态

## 测试防轰炸机制

运行测试脚本验证功能：

```bash
python test_rate_limiter.py
```

测试内容包括：
- 正常请求处理
- 速率限制触发
- 恶意内容检测
- 并发请求处理

## 部署注意事项

### Redis配置

确保Redis服务器正常运行：

```python
# 在 config.py 中配置
REDIS_CONFIG = {
    "HOST": "localhost",
    "PORT": 6380,
    "PASSWORD": "your_password",
    "DB": 0
}
```

### 生产环境调整

1. **调整限制阈值**: 根据实际流量调整限制值
2. **启用日志记录**: 监控异常请求
3. **配置告警**: 设置异常流量告警
4. **备份Redis数据**: 定期备份限制数据

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务器状态
   - 验证连接配置
   - 查看防火墙设置

2. **限制不生效**
   - 确认Redis数据持久化
   - 检查时间窗口设置
   - 验证IP地址获取逻辑

3. **误报限制**
   - 调整限制阈值
   - 检查网络代理设置
   - 验证客户端识别逻辑

### 日志调试

启用详细日志记录：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 安全建议

1. **定期更新**: 保持依赖库最新版本
2. **监控流量**: 设置流量监控和告警
3. **备份配置**: 定期备份限制配置
4. **测试验证**: 定期进行安全测试
5. **多层防护**: 结合WAF等安全措施

## 扩展功能

可以根据需要扩展以下功能：

- **用户身份验证**: 基于用户ID的限制
- **地理位置限制**: 基于地理位置的访问控制  
- **行为分析**: 基于用户行为的智能限制
- **机器学习**: 使用ML模型检测异常流量

## 联系我们

如有问题或建议，请通过以下方式联系：
- 邮箱: your-email@example.com
- GitHub: 提交Issue或Pull Request

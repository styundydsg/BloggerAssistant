"""
邮件发送示例 - 演示如何使用call_blogger发送邮件到QQ邮箱
"""

import os
import sys

# 添加lib目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

from modules.notice_service import call_blogger

def main():
    """主函数 - 演示邮件发送功能"""
    
    # 方法1: 使用默认配置发送邮件
    print("=== 方法1: 使用默认配置发送邮件 ===")
    result = call_blogger()
    print(result)
    print()
    
    # 方法2: 自定义邮件内容
    print("=== 方法2: 自定义邮件内容 ===")
    custom_message = """
    尊敬的博主：
    
    我是您的博客读者，通过博客系统联系您。
    我对您最近发布的关于人工智能的文章非常感兴趣，希望了解更多相关内容。
    
    期待您的回复！
    
    此致
    敬礼
    
    读者
    """
    result = call_blogger(message=custom_message)
    print(result)
    print()
    
    # 方法3: 发送到特定QQ邮箱
    print("=== 方法3: 发送到特定QQ邮箱 ===")
    qq_email = "your_qq_email@qq.com"  # 请替换为实际的QQ邮箱
    result = call_blogger(
        message="测试邮件发送功能", 
        recipient_email=qq_email
    )
    print(result)

if __name__ == "__main__":
    # 设置环境变量（在实际使用中，建议在系统环境变量中设置）
    os.environ["SENDER_EMAIL"] = "your_email@qq.com"  # 请替换为发件人QQ邮箱
    os.environ["SENDER_PASSWORD"] = "your_authorization_code"  # 请替换为QQ邮箱授权码
    os.environ["RECIPIENT_EMAIL"] = "recipient@qq.com"  # 请替换为收件人QQ邮箱
    
    main()

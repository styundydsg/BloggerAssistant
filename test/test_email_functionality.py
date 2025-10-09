"""
邮件功能测试脚本
测试call_blogger函数是否能正常发送邮件到QQ邮箱
"""

import os
import sys

# 添加lib目录到Python路径
sys.path.append('lib')

from modules.notice_service import call_blogger

def test_email_functionality():
    """测试邮件发送功能"""
    print("=== 邮件发送功能测试 ===\n")
    
    # 检查环境变量是否设置
    required_vars = ["SENDER_EMAIL", "SENDER_PASSWORD", "RECIPIENT_EMAIL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  警告：以下环境变量未设置：")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请在运行测试前设置这些环境变量。")
        print("参考 docs/email_configuration.md 获取配置指南。")
        return
    
    print("✅ 环境变量检查通过")
    print(f"发件人: {os.getenv('SENDER_EMAIL')}")
    print(f"收件人: {os.getenv('RECIPIENT_EMAIL')}")
    print()
    
    # 测试1: 发送简单测试邮件
    print("=== 测试1: 发送简单测试邮件 ===")
    try:
        result = call_blogger(message="这是一封测试邮件，用于验证博客系统的邮件发送功能。")
        print(f"结果: {result}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print()
    
    # 测试2: 发送详细测试邮件
    print("=== 测试2: 发送详细测试邮件 ===")
    detailed_message = """
博客系统邮件功能测试

这是一封详细的测试邮件，用于验证以下功能：
- SMTP连接正常
- 认证成功
- 邮件内容正确编码
- 邮件发送成功

测试时间: 2025年9月25日
系统状态: 正常

如果收到此邮件，说明邮件发送功能工作正常。
"""
    try:
        result = call_blogger(message=detailed_message)
        print(f"结果: {result}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    # 提示用户设置环境变量
    print("邮件发送功能测试")
    print("=" * 50)
    print("在运行测试前，请确保已设置以下环境变量：")
    print("1. SENDER_EMAIL - 发件人QQ邮箱")
    print("2. SENDER_PASSWORD - QQ邮箱授权码") 
    print("3. RECIPIENT_EMAIL - 收件人邮箱")
    print("\n设置方法参考 docs/email_configuration.md")
    print("=" * 50)
    
    input("按Enter键开始测试...")
    test_email_functionality()

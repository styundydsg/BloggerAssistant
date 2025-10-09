import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from .config import CONFIG

def send_email(subject, message, recipient_email=None):
    """
    发送邮件到指定邮箱
    
    Args:
        subject: 邮件主题
        message: 邮件内容
        recipient_email: 收件人邮箱，如果为None则使用配置中的默认邮箱
    
    Returns:
        str: 发送结果信息
    """
    try:
        email_config = CONFIG["EMAIL_CONFIG"]
        
        # 获取配置信息
        smtp_server = email_config["SMTP_SERVER"]
        smtp_port = email_config["SMTP_PORT"]
        sender_email = email_config["SENDER_EMAIL"]
        sender_password = email_config["SENDER_PASSWORD"]
        recipient = recipient_email or email_config["RECIPIENT_EMAIL"]
        
        # 检查必要的配置
        if not sender_email or not sender_password:
            return "错误：未配置发件人邮箱或密码，请设置SENDER_EMAIL和SENDER_PASSWORD环境变量"
        
        if not recipient:
            return "错误：未配置收件人邮箱，请设置RECIPIENT_EMAIL环境变量"
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加邮件正文
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 启用TLS加密
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return f"邮件发送成功！已发送到: {recipient}"
        
    except smtplib.SMTPAuthenticationError:
        return "错误：SMTP认证失败，请检查邮箱和密码是否正确"
    except smtplib.SMTPException as e:
        return f"错误：邮件发送失败 - {str(e)}"
    except Exception as e:
        return f"错误：发生未知错误 - {str(e)}"

def call_blogger(message="用户通过博客系统联系您", recipient_email=None):
    """
    联系博主 - 发送邮件通知
    
    Args:
        message: 邮件内容，默认为基本联系信息
        recipient_email: 收件人邮箱，如果为None则使用配置中的默认邮箱
    
    Returns:
        str: 发送结果信息
    """
    subject = "博客系统联系通知"
    return send_email(subject, message, recipient_email)

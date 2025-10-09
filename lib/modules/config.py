"""配置文件模块 - 处理应用配置和常量设置"""

import os
import sys

# 基础路径设置
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
lib_dir = os.path.join(parent_dir, 'lib')
model_dir = os.path.join(parent_dir, 'model')
blog_files_path = os.path.join(parent_dir, 'blog_files')
vectorstore_path = os.path.join(lib_dir, 'faiss_index')

# 添加lib目录到Python路径
sys.path.append(lib_dir)

# Redis配置
REDIS_CONFIG = {
    "HOST": os.getenv("REDIS_HOST", "localhost"),
    "PORT": int(os.getenv("REDIS_PORT", 6380)),
    "DB": int(os.getenv("REDIS_DB", 0)),
    "PASSWORD": os.getenv("REDIS_PASSWORD", "123456"),
    "DECODE_RESPONSES": True
}

# 邮件配置
EMAIL_CONFIG = {
    "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.qq.com"),
    "SMTP_PORT": int(os.getenv("SMTP_PORT", 587)),
    "SENDER_EMAIL": os.getenv("SENDER_EMAIL","2983105040@qq.com"),
    "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD","hjbqijsuqgpzdeie"),
    "RECIPIENT_EMAIL": os.getenv("RECIPIENT_EMAIL", "2983105040@qq.com")
}

# 应用配置
CONFIG = {
    "API_KEY": os.getenv("DEEPSEEK_API_KEY"),
    "BASE_URL": "https://api.deepseek.com",
    "HISTORY_DIR": os.path.expanduser("~/deepseek_chat_history"),
    "MODEL_MAPPING": {
        "V3": "deepseek-chat",
        "R1": "deepseek-reasoner"
    },
    "VECTORSTORE_PATH": vectorstore_path,
    "BLOG_FILES_PATH": blog_files_path,
    "MODEL_DIR": model_dir,
    "REDIS_CONFIG": REDIS_CONFIG,
    "EMAIL_CONFIG": EMAIL_CONFIG
}

# 模板配置
DELIMITER = "####"

# 提示词模板
QA_TEMPLATE = """基于以下文档内容，生成一个问题及其答案：\
{doc}\
\
请严格使用以下格式：\
QUESTION: [你的问题]\
ANSWER: [对应的答案]"""

RETRIEVAL_TEMPLATE = """\
使用以下上下文回答问题。如果你不知道答案，就说不知道。如果对方说的话让你感到疑惑\
\
上下文:\
{context}\
\
问题: {question}\
答案:\
"""

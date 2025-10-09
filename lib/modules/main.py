"""主业务逻辑模块 - 整合所有功能并提供简洁的API"""

from typing import Optional
from langchain_community.vectorstores import FAISS
import os
import datetime
from .config import CONFIG
from .vectorstore_manager import initialize_vectorstore
from .qa_chain import create_llm, create_qa_chain
from .check_instruction import check
from .intent_recognition import recognize_intent, is_contact_intent, get_contact_response
from langchain.prompts import PromptTemplate
from .notice_service import call_blogger
import socketserver

class ContactBloggerTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # 获取客户端数据
        data = self.request.recv(1024).strip()
        print(f"来自 {self.client_address[0]} 的数据: {data.decode('utf-8')}")
        
        # 发送响应
        self.request.sendall(b"Message received")

# 全局变量用于缓存
_vectorstore: Optional[FAISS] = None
_qa_chain = None
_Blogger_is_online = True  # 博主在线状态，默认为False



def initialize_system():
    """初始化整个系统"""
    global _vectorstore, _qa_chain
    
    print("正在初始化系统...")
    
    # 初始化向量数据库
    _vectorstore = initialize_vectorstore()
    
    # 创建语言模型
    llm = create_llm()
    
    # 创建问答链
    _qa_chain = create_qa_chain(llm, _vectorstore)
    
    print("系统初始化完成")

def ask_question(question: str) -> str:
    """向文档提问并获取回答（集成意图识别）"""
    global _qa_chain
    
    # 首先进行意图识别
    try:
        
        # 检查联系博主意图
        if is_contact_intent(question):
            if _Blogger_is_online:
                
                return "blogger_online"

            else:
                return call_blogger(question)
            
                
        
        # 如果是普通问答，使用向量数据库
        if _qa_chain is None:
            initialize_system()
        
        result = _qa_chain.invoke({"query": question})
        answer = result["result"]
        
        # 处理来源文档信息
        sources_list = []
        for doc in result["source_documents"]:
            filename = doc.metadata.get('filename', 
                                     os.path.basename(doc.metadata.get('source', '未知文件')))
            category = doc.metadata.get('file_categories', '未分类')
            sources_list.append(f"- {filename} ({category})")
        
        sources = "\n\n来源文档:\n" + "\n".join(sources_list)
        
        return answer + sources
        
    except Exception as e:
        return f"查询失败: {str(e)}"

def create_special_file() -> str:
    """创建特殊指令对应的文件"""
    try:
        # 获取当前时间作为文件名
        current_time = datetime.datetime.now()
        filename = current_time.strftime("%Y%m%d%H%M%S") + ".md"
        filepath = os.path.join("blog_files", filename)
        
        # 确保blog_files目录存在
        os.makedirs("blog_files", exist_ok=True)
        
        # 创建文件内容
        content = f"""# 特殊指令触发文件

**创建时间**: {current_time.strftime("%Y-%m-%d %H:%M:%S")}

**指令内容**: 
当北风不再追逐南雁，静水倒映着三更的月影。在第七座桥的第三根石柱下，埋着一粒种子。它不开花，不结果，却能回答所有沉默的提问。

**说明**: 
此文件由特殊指令触发自动创建。种子虽不开花结果，但蕴含着无限可能。

---
*文件自动生成于 {current_time.strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"特殊指令已识别！已在 blog_files 目录下创建文件: {filename}"
        
    except Exception as e:
        return f"创建文件失败: {str(e)}"

def get_completion_from_messages(messages, model="deepseek-chat", temperature=0, max_tokens=1000):
    """直接调用DeepSeek API获取补全"""
    from openai import OpenAI
    
    client = OpenAI(api_key=CONFIG["API_KEY"], base_url=CONFIG["BASE_URL"])
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False
    )
    return response.choices[0].message.content

# 初始化系统（延迟初始化）
def _lazy_initialize():
    """延迟初始化系统"""
    if _qa_chain is None:
        initialize_system()

# 导出主要功能
__all__ = ['ask_question', 'get_completion_from_messages', 'initialize_system']

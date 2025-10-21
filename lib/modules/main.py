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
        intent_result = recognize_intent(question)
        intent = intent_result.get("intent", "技术问答")
        confidence = intent_result.get("confidence", 0.5)
        
        print(f"意图识别结果: {intent}, 置信度: {confidence}")
        
        # 根据意图类型处理
        if intent == "联系博主":
            # 联系博主意图，返回特殊标识
            return "blogger_online"
        elif intent == "一般聊天":
            # 一般聊天意图，返回友好响应
            return "你好！我是博客助手，很高兴和你聊天。有什么我可以帮助你的吗？"
        elif intent == "个人咨询":
            # 个人咨询意图，返回标准响应
            return "关于博主个人的问题，建议直接通过联系方式与博主交流。"
        else:
            # 技术问答、博客内容查询等意图，使用向量数据库
            if _qa_chain is None:
                initialize_system()
            
            result = _qa_chain.invoke({"query": question})
            answer = result["result"]
            
            # 处理来源文档信息 - 去重
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


# 导出主要功能
__all__ = ['ask_question', 'initialize_system']

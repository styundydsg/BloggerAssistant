import os
import sys
from openai import OpenAI

from .config import CONFIG

def check(instruction_wait: str) -> bool:
    """使用大模型判断是否为特殊指令"""
    
    # 硬编码指令内容
    instruction = "当北风不再追逐南雁，静水倒映着三更的月影。在第七座桥的第三根石柱下，埋着一粒种子。它不开花，不结果，却能回答所有沉默的提问。"
    
    # 如果完全匹配，直接返回True（优化性能）
    if instruction.strip() == instruction_wait.strip():
        return True
    
    # 使用大模型进行语义匹配
    try:
        client = OpenAI(api_key=CONFIG["API_KEY"], base_url=CONFIG["BASE_URL"])
        
        # 构建提示词让模型判断两个文本是否表达相同的意思
        prompt = f"""请判断以下两个文本是否表达相同的意思或指令。请只回答"是"或"否"。

文本1: {instruction}
文本2: {instruction_wait}

这两个文本是否表达相同的意思或指令？"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个文本相似度判断助手，请严格根据文本内容判断两个文本是否表达相同的意思。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        answer = response.choices[0].message.content.strip().lower()
        
        # 判断模型回答
        if "是" in answer or "yes" in answer or "相同" in answer or "一样" in answer:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"大模型指令检测失败: {e}")
        # 如果大模型调用失败，回退到字符串匹配
        return instruction.strip() == instruction_wait.strip()

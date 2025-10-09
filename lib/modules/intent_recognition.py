"""意图识别模块 - 识别用户输入中的各种意图"""

import json
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import CONFIG




class IntentRecognizer:
    """意图识别器"""
    
    def __init__(self):
        self.client = OpenAI(api_key=CONFIG["API_KEY"], base_url=CONFIG["BASE_URL"])
        self.intent_prompt_template = """你是一位博客问答助手。你的任务是分析用户的输入，识别其意图，并提取出相关的关键信息（槽位）。

意图列表：
1. 联系博主 - 用户想要联系博主或寻求人工帮助
2. 普通问答 - 用户想要获取博客相关的信息或答案
3. 特殊指令 - 用户输入了特殊指令

请严格按照JSON格式输出，包含以下字段：
- "intent": 识别的意图（"联系博主"、"普通问答"、"特殊指令"）
- "slots": 包含提取的关键信息，如联系方式、问题类型等
- "confidence": 置信度（0-1之间的浮点数）

如果某个槽位不存在，请设为 null。

示例：
输入：我需要人工服务
输出：{{"intent": "联系博主", "slots": {{"contact_method": "人工服务"}}, "confidence": 0.95}}

输入：博客里讲了什么内容
输出：{{"intent": "普通问答", "slots": {{"question_type": "内容查询"}}, "confidence": 0.9}}

输入：当北风不再追逐南雁
输出：{{"intent": "特殊指令", "slots": {{"instruction_type": "特殊指令"}}, "confidence": 1.0}}

现在请分析以下输入：
输入：{user_input}
输出："""

    def recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """识别用户输入的意图"""
        try:
            # 使用大模型进行意图识别
            prompt = self.intent_prompt_template.format(user_input=user_input)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的意图识别助手，请准确识别用户意图并提取关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON响应
            try:
                # 清理响应文本，移除可能的引号问题
                cleaned_text = result_text.strip()
                if cleaned_text.startswith('"') and cleaned_text.endswith('"'):
                    cleaned_text = cleaned_text[1:-1]
                
                result = json.loads(cleaned_text)
                return result
            except json.JSONDecodeError as je:
                print(f"JSON解析失败，使用回退方法: {je}")
                # 如果JSON解析失败，使用启发式规则
                return self._fallback_intent_recognition(user_input)
                
        except Exception as e:
            print(f"意图识别失败: {e}")
            return self._fallback_intent_recognition(user_input)
    
    def _fallback_intent_recognition(self, user_input: str) -> Dict[str, Any]:
        """回退的意图识别方法（基于关键词）"""
        user_input_lower = user_input.lower()
        
        # 联系博主的关键词
        contact_keywords = [
            '联系', '博主', '人工', '客服', '帮助', '支持', 'email', '邮箱', 
            '微信', 'qq', '电话', '联系方式', 'contact', 'help', 'support'
        ]
        
        
        # 检查联系博主意图
        contact_score = sum(1 for keyword in contact_keywords if keyword in user_input_lower)
        if contact_score > 0:
            return {
                "intent": "联系博主",
                "slots": {"contact_method": "关键词匹配"},
                "confidence": min(0.7 + contact_score * 0.1, 0.95)
            }
        
        # 默认为普通问答
        return {
            "intent": "普通问答",
            "slots": {"question_type": "一般问题"},
            "confidence": 0.8
        }
    
    def is_contact_intent(self, user_input: str) -> bool:
        """判断是否为联系博主意图"""
        intent_result = self.recognize_intent(user_input)
        return intent_result.get("intent") == "联系博主"
    
    def get_contact_response(self, user_input: str) -> str:
        """生成联系博主的响应"""
        intent_result = self.recognize_intent(user_input)
        
        if intent_result.get("intent") == "联系博主":
            slots = intent_result.get("slots", {})
            contact_method = slots.get("contact_method", "一般联系")
            
            response = f"""我识别到您想要{contact_method}。以下是联系博主的方式：

📧 邮箱：jasonh0401@163.com
📱 QQ：2983105040

"""
            
            return response
        else:
            return "当前未识别到联系博主的意图。"

# 创建全局实例
_intent_recognizer = None

def get_intent_recognizer() -> IntentRecognizer:
    """获取意图识别器实例（单例模式）"""
    global _intent_recognizer
    if _intent_recognizer is None:
        _intent_recognizer = IntentRecognizer()
    return _intent_recognizer

def recognize_intent(user_input: str) -> Dict[str, Any]:
    """识别用户意图的便捷函数"""
    recognizer = get_intent_recognizer()
    return recognizer.recognize_intent(user_input)

def is_contact_intent(user_input: str) -> bool:
    """判断是否为联系博主意图的便捷函数"""
    recognizer = get_intent_recognizer()
    return recognizer.is_contact_intent(user_input)

def get_contact_response(user_input: str) -> str:
    """获取联系博主响应的便捷函数"""
    recognizer = get_intent_recognizer()
    return recognizer.get_contact_response(user_input)

# 导出主要功能
__all__ = [
    'IntentRecognizer', 
    'recognize_intent', 
    'is_contact_intent', 
    'get_contact_response'
]

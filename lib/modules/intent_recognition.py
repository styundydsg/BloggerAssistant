"""意图识别模块 - 修复版本"""

import json
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Optional
import os
import pickle
import logging
import re
from pathlib import Path
from collections import Counter
import jieba
from .config import CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 解决numpy兼容性问题
try:
    np.importlib.reload(np)
except:
    pass


class SimpleIntentClassifier(nn.Module):
    """简化意图分类器模型"""
    
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int, 
                 output_dim: int, n_layers: int, dropout: float):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # 如果只有一层，不使用dropout
        if n_layers == 1:
            dropout = 0.0
            
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, n_layers, 
                           dropout=dropout, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text: torch.Tensor) -> torch.Tensor:
        embedded = self.dropout(self.embedding(text))
        output, (hidden, cell) = self.lstm(embedded)
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        return self.fc(hidden)


class SimpleVocabulary:
    """简化词汇表处理"""
    
    def __init__(self):
        self.word2idx = {}
        self.idx2word = {}
        self.word_counts = Counter()
        self.pad_token = '<PAD>'
        self.unk_token = '<UNK>'
        self._build_basic_vocab()
    
    def _build_basic_vocab(self):
        """构建基础词汇表"""
        basic_tokens = [self.pad_token, self.unk_token]
        for idx, token in enumerate(basic_tokens):
            self.word2idx[token] = idx
            self.idx2word[idx] = token
    
    def build_vocab(self, texts: List[str], min_freq: int = 1):  # 降低最小词频
        """从文本构建词汇表"""
        # 重置词汇表
        self.word2idx = {self.pad_token: 0, self.unk_token: 1}
        self.idx2word = {0: self.pad_token, 1: self.unk_token}
        self.word_counts = Counter()
        
        # 统计词频
        for text in texts:
            tokens = self.tokenize(text)
            self.word_counts.update(tokens)
        
        # 添加满足最小词频的词
        idx = 2
        for word, count in self.word_counts.items():
            if count >= min_freq:
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                idx += 1
        
        logger.info(f"词汇表构建完成，词汇量: {len(self.word2idx)}")
    
    def tokenize(self, text: str) -> List[str]:
        """中文分词"""
        try:
            # 使用jieba分词，启用HMM以提高分词准确性
            return list(jieba.cut(text, HMM=True))
        except Exception as e:
            logger.warning(f"jieba分词失败: {e}，使用简单分词")
            # 回退到简单分词：按字符分割
            return [char for char in text if char.strip()]
    
    def numericalize(self, text: str, max_length: int = 50) -> List[int]:
        """将文本转换为数字序列"""
        tokens = self.tokenize(text)
        numericalized = []
        
        for token in tokens:
            if token in self.word2idx:
                numericalized.append(self.word2idx[token])
            else:
                numericalized.append(self.word2idx[self.unk_token])
        
        # 填充或截断
        if len(numericalized) < max_length:
            numericalized.extend([self.word2idx[self.pad_token]] * (max_length - len(numericalized)))
        else:
            numericalized = numericalized[:max_length]
        
        return numericalized
    
    def __len__(self):
        return len(self.word2idx)


class SimpleIntentRecognizer:
    """基于PyTorch的简化意图识别器"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"使用设备: {self.device}")
        
        self.model: Optional[SimpleIntentClassifier] = None
        self.vocab: Optional[SimpleVocabulary] = None
        self.intent_labels: Optional[List[str]] = None
        
        self.model_dir = Path(CONFIG["MODEL_DIR"])
        self.model_path = self.model_dir / "simple_intent_classifier.pth"
        self.vocab_path = self.model_dir / "simple_vocab.pkl"
        self.training_data_path = Path(__file__).parent.parent.parent / "intent_training_data.json"
        
        # 模型参数 - 优化配置
        self.embedding_dim = 50   # 减小嵌入维度
        self.hidden_dim = 64      # 减小隐藏层大小
        self.output_dim = 5       # 5种意图类型
        self.n_layers = 1         # 单层LSTM
        self.dropout = 0.2        # 减小dropout
        self.batch_size = 8       # 减小批大小
        self.epochs = 20          # 减少训练轮数
        self.max_length = 30      # 减小序列长度
        self.learning_rate = 0.001
        
        # 意图关键词映射
        self._setup_intent_keywords()
        self._load_or_train_model()
    
    def _setup_intent_keywords(self):
        """设置意图关键词映射"""
        self.contact_keywords = [
            '联系', '博主', '人工', '客服', '帮助', '支持', 'email', '邮箱', 
            '微信', 'qq', '电话', '联系方式', 'contact', 'help', 'support',
            '联系你', '找你', '找你', '找你'
        ]
        
        self.tech_keywords = {
            "编程语言": ["python", "java", "c++", "c语言", "javascript", "typescript", "编程", "代码"],
            "操作系统": ["linux", "windows", "macos", "unix", "xv6", "openharmony", "系统", "操作系统"],
            "开发工具": ["git", "docker", "vscode", "ide", "编译器", "工具"],
            "硬件": ["芯片", "处理器", "内存", "硬盘", "主板", "硬件"],
            "网络": ["tcp", "udp", "http", "https", "协议", "网络"]
        }
        
        self.question_types = {
            "概念解释": ["什么", "是什么", "定义", "概念", "意思", "含义"],
            "使用方法": ["怎么", "如何", "使用", "用法", "怎样", "操作"],
            "问题解决": ["解决", "错误", "问题", "失败", "怎么办", "为啥", "为什么"],
            "代码示例": ["代码", "示例", "实例", "demo", "例子", "源码"]
        }
        
        # 意图优先级映射
        self.intent_priority = {
            "联系博主": 3,  # 最高优先级
            "博客内容查询": 2,
            "技术问答": 1   # 默认优先级
        }
    
    def _load_or_train_model(self):
        """加载或训练模型"""
        try:
            # 确保模型目录存在
            self.model_dir.mkdir(parents=True, exist_ok=True)
            
            if self._model_files_exist():
                self._load_model()
                logger.info("意图识别模型加载成功")
            else:
                logger.info("未找到预训练模型，开始训练...")
                self._train_model()
                
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            # 即使训练失败，也允许使用关键词回退
            logger.info("将使用关键词回退模式")
    
    def _model_files_exist(self) -> bool:
        """检查模型文件是否存在"""
        return self.model_path.exists() and self.vocab_path.exists()
    
    def _load_training_data(self) -> List[Dict]:
        """加载训练数据"""
        if not self.training_data_path.exists():
            logger.warning(f"训练数据文件不存在: {self.training_data_path}")
            # 创建默认训练数据
            return self._create_default_training_data()
        
        try:
            with open(self.training_data_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            train_data = []
            for item in training_data.get("training_data", []):
                train_data.append({
                    "text": item["input"],
                    "label": item["intent"]
                })
            
            logger.info(f"加载了 {len(train_data)} 条训练数据")
            return train_data
            
        except Exception as e:
            logger.error(f"加载训练数据失败: {e}")
            return self._create_default_training_data()
    
    def _create_default_training_data(self) -> List[Dict]:
        """创建默认训练数据"""
        default_data = [
            {"text": "怎么联系博主", "label": "联系博主"},
            {"text": "有微信吗", "label": "联系博主"},
            {"text": "邮箱是多少", "label": "联系博主"},
            {"text": "怎么找你", "label": "联系博主"},
            {"text": "Python编程问题", "label": "技术问答"},
            {"text": "什么是机器学习", "label": "技术问答"},
            {"text": "怎么使用git", "label": "技术问答"},
            {"text": "代码报错怎么办", "label": "技术问答"},
            {"text": "查看博客文章", "label": "博客内容查询"},
            {"text": "有什么技术教程", "label": "博客内容查询"},
            {"text": "学习笔记", "label": "博客内容查询"}
        ]
        logger.info("使用默认训练数据")
        return default_data
    
    def _prepare_training_data(self):
        """准备训练数据"""
        train_data = self._load_training_data()
        
        if not train_data:
            raise ValueError("没有可用的训练数据")
        
        # 提取文本和标签
        texts = [item["text"] for item in train_data]
        labels = [item["label"] for item in train_data]
        
        # 构建词汇表
        self.vocab = SimpleVocabulary()
        self.vocab.build_vocab(texts, min_freq=1)  # 降低最小词频
        
        # 构建标签映射
        unique_labels = list(set(labels))
        self.intent_labels = unique_labels
        self.output_dim = len(unique_labels)
        self.label2idx = {label: idx for idx, label in enumerate(unique_labels)}
        self.idx2label = {idx: label for label, idx in self.label2idx.items()}
        
        logger.info(f"训练数据: {len(texts)} 条文本, {len(unique_labels)} 种意图: {unique_labels}")
        
        return texts, labels
    
    def _create_data_loader(self, texts: List[str], labels: List[str]):
        """创建数据加载器"""
        # 转换为数值序列
        text_sequences = []
        label_indices = []
        
        for text, label in zip(texts, labels):
            numericalized = self.vocab.numericalize(text, self.max_length)
            text_sequences.append(numericalized)
            label_indices.append(self.label2idx[label])
        
        # 转换为tensor
        text_tensor = torch.LongTensor(text_sequences)
        label_tensor = torch.LongTensor(label_indices)
        
        # 创建简单数据集
        dataset = torch.utils.data.TensorDataset(text_tensor, label_tensor)
        data_loader = torch.utils.data.DataLoader(
            dataset, 
            batch_size=self.batch_size,
            shuffle=True
        )
        
        return data_loader
    
    def _train_model(self):
        """训练模型"""
        logger.info("开始训练意图识别模型...")
        
        try:
            # 准备数据
            texts, labels = self._prepare_training_data()
            data_loader = self._create_data_loader(texts, labels)
            
            # 初始化模型
            vocab_size = len(self.vocab)
            self.model = SimpleIntentClassifier(
                vocab_size, 
                self.embedding_dim, 
                self.hidden_dim, 
                self.output_dim, 
                self.n_layers, 
                self.dropout
            )
            self.model = self.model.to(self.device)
            
            # 训练过程
            optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
            criterion = nn.CrossEntropyLoss()
            
            self.model.train()
            for epoch in range(self.epochs):
                total_loss = 0
                correct_predictions = 0
                total_predictions = 0
                
                for batch_texts, batch_labels in data_loader:
                    batch_texts = batch_texts.to(self.device)
                    batch_labels = batch_labels.to(self.device)
                    
                    optimizer.zero_grad()
                    predictions = self.model(batch_texts)
                    loss = criterion(predictions, batch_labels)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                    optimizer.step()
                    
                    total_loss += loss.item()
                    
                    # 计算准确率
                    _, predicted = torch.max(predictions, 1)
                    correct_predictions += (predicted == batch_labels).sum().item()
                    total_predictions += batch_labels.size(0)
                
                accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
                avg_loss = total_loss / len(data_loader)
                
                if (epoch + 1) % 5 == 0:
                    logger.info(f'Epoch: {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}')
            
            # 保存模型
            self._save_model()
            logger.info("模型训练完成")
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            # 训练失败时，设置模型为None，使用回退方法
            self.model = None
    
    def _save_model(self):
        """保存模型和词汇表"""
        try:
            # 保存模型
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_config': {
                    'embedding_dim': self.embedding_dim,
                    'hidden_dim': self.hidden_dim,
                    'output_dim': self.output_dim,
                    'n_layers': self.n_layers,
                    'dropout': self.dropout
                }
            }, self.model_path)
            
            # 保存词汇表和标签
            vocab_data = {
                'vocab': self.vocab,
                'intent_labels': self.intent_labels,
                'label2idx': self.label2idx,
                'idx2label': self.idx2label
            }
            with open(self.vocab_path, 'wb') as f:
                pickle.dump(vocab_data, f)
                
            logger.info(f"模型和词汇表已保存")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            raise
    
    def _load_model(self):
        """加载模型和词汇表"""
        try:
            # 加载词汇表和标签
            with open(self.vocab_path, 'rb') as f:
                vocab_data = pickle.load(f)
            
            self.vocab = vocab_data['vocab']
            self.intent_labels = vocab_data['intent_labels']
            self.label2idx = vocab_data['label2idx']
            self.idx2label = vocab_data['idx2label']
            self.output_dim = len(self.intent_labels)
            
            # 加载模型配置
            checkpoint = torch.load(self.model_path, map_location=self.device)
            model_config = checkpoint['model_config']
            
            # 初始化模型
            vocab_size = len(self.vocab)
            self.model = SimpleIntentClassifier(
                vocab_size,
                model_config['embedding_dim'],
                model_config['hidden_dim'],
                model_config['output_dim'],
                model_config['n_layers'],
                model_config['dropout']
            )
            
            # 加载模型权重
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            self.model = None
    
    def preprocess_text(self, text: str) -> torch.Tensor:
        """预处理文本"""
        if self.vocab is None:
            raise ValueError("词汇表未初始化")
        
        numericalized = self.vocab.numericalize(text, self.max_length)
        tensor = torch.LongTensor(numericalized).unsqueeze(0).to(self.device)
        return tensor
    
    def recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """识别用户输入的意图"""
        # 如果模型不可用，直接使用回退方法
        if self.model is None or self.vocab is None:
            return self._fallback_intent_recognition(user_input)
        
        try:
            # 预处理文本
            text_tensor = self.preprocess_text(user_input)
            
            # 预测
            with torch.no_grad():
                prediction = self.model(text_tensor)
                probabilities = torch.softmax(prediction, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
            
            intent_idx = predicted_idx.item()
            confidence_score = confidence.item()
            
            # 获取意图标签
            if 0 <= intent_idx < len(self.intent_labels):
                intent = self.idx2label[intent_idx]
            else:
                intent = "技术问答"
                confidence_score = 0.5
            
            # 使用关键词增强置信度
            enhanced_result = self._enhance_with_keywords(user_input, intent, confidence_score)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            return self._fallback_intent_recognition(user_input)
    
    def _enhance_with_keywords(self, user_input: str, intent: str, confidence: float) -> Dict[str, Any]:
        """使用关键词增强识别结果"""
        keyword_boost = self._calculate_keyword_boost(user_input, intent)
        enhanced_confidence = min(confidence + keyword_boost, 0.95)
        
        # 提取槽位信息
        slots = self._extract_slots(user_input, intent)
        
        # 如果关键词匹配很强，可以覆盖模型结果
        if keyword_boost > 0.3 and enhanced_confidence > 0.7:
            model_used = "enhanced_neural_network"
        elif confidence < 0.6:
            # 置信度太低，使用回退
            return self._fallback_intent_recognition(user_input)
        else:
            model_used = "neural_network"
        
        return {
            "intent": intent,
            "slots": slots,
            "confidence": enhanced_confidence,
            "model_used": model_used
        }
    
    def _calculate_keyword_boost(self, user_input: str, intent: str) -> float:
        """计算关键词增强分数"""
        user_input_lower = user_input.lower()
        boost = 0.0
        
        if intent == "联系博主":
            contact_matches = sum(1 for keyword in self.contact_keywords if keyword in user_input_lower)
            boost = contact_matches * 0.1
        
        elif intent == "技术问答":
            # 检查技术关键词
            for keywords in self.tech_keywords.values():
                if any(keyword in user_input_lower for keyword in keywords):
                    boost += 0.1
                    break
            
            # 检查问题类型关键词
            for keywords in self.question_types.values():
                if any(keyword in user_input_lower for keyword in keywords):
                    boost += 0.1
                    break
        
        return min(boost, 0.3)  # 最大增强0.3
    
    def _extract_slots(self, text: str, intent: str) -> Dict[str, str]:
        """提取槽位信息"""
        slots = {}
        text_lower = text.lower()
        
        if intent == "技术问答":
            self._extract_technology_slots(text_lower, slots)
            self._extract_question_slots(text_lower, slots)
        
        elif intent == "博客内容查询":
            self._extract_content_slots(text_lower, slots)
        
        elif intent == "联系博主":
            self._extract_contact_slots(text_lower, slots)
        
        elif intent == "个人咨询":
            self._extract_personal_slots(text_lower, slots)
        
        elif intent == "一般聊天":
            self._extract_chat_slots(text_lower, slots)
        
        return slots
    
    def _extract_technology_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取技术相关槽位"""
        for tech_type, keywords in self.tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["technology_type"] = tech_type
                break
    
    def _extract_question_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取问题类型槽位"""
        for q_type, keywords in self.question_types.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["question_type"] = q_type
                break
    
    def _extract_content_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取内容类型槽位"""
        content_types = {
            "技术教程": ["教程", "指南", "教学", "怎么", "如何"],
            "学习笔记": ["笔记", "学习", "记录", "总结"],
            "个人日记": ["日记", "心情", "感悟", "生活"],
            "问题解决": ["解决", "问题", "错误", "bug", "故障"]
        }
        
        for c_type, keywords in content_types.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["content_type"] = c_type
                break
    
    def _extract_contact_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取联系方式槽位"""
        contact_methods = {
            "邮箱": ["邮箱", "email", "mail"],
            "微信": ["微信", "wechat"],
            "QQ": ["qq", "扣扣"],
            "人工服务": ["人工", "客服", "支持"]
        }
        
        for method, keywords in contact_methods.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["contact_method"] = method
                break
    
    def _extract_personal_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取个人咨询槽位"""
        personal_aspects = {
            "工作": ["工作", "职业", "岗位", "公司", "上班"],
            "学习": ["学习", "学习经历", "教育", "学校", "课程"],
            "生活": ["生活", "日常", "爱好", "兴趣", "习惯"],
            "规划": ["规划", "计划", "目标", "未来", "发展"],
            "建议": ["建议", "意见", "推荐", "指导", "帮助"]
        }
        
        for aspect, keywords in personal_aspects.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["aspect"] = aspect
                break
    
    def _extract_chat_slots(self, text_lower: str, slots: Dict[str, str]):
        """提取一般聊天槽位"""
        chat_types = {
            "问候": ["你好", "在吗", "早上好", "晚上好", "hi", "hello"],
            "感谢": ["谢谢", "感谢", "多谢", "thx", "thanks"],
            "闲聊": ["最近", "怎么样", "还好吗", "忙吗"],
            "关心": ["注意", "保重", "照顾好", "小心"]
        }
        
        for chat_type, keywords in chat_types.items():
            if any(keyword in text_lower for keyword in keywords):
                slots["chat_type"] = chat_type
                break
    
    def _fallback_intent_recognition(self, user_input: str) -> Dict[str, Any]:
        """回退的意图识别方法（基于关键词）"""
        user_input_lower = user_input.lower()
        
        # 计算各意图的匹配分数
        intent_scores = {}
        
        # 联系博主意图
        contact_score = sum(1 for keyword in self.contact_keywords if keyword in user_input_lower)
        intent_scores["联系博主"] = contact_score
        
        # 博客内容查询
        blog_keywords = ['博客', '文章', '帖子', 'blog', 'post', '写作', '内容']
        blog_score = sum(1 for keyword in blog_keywords if keyword in user_input_lower)
        intent_scores["博客内容查询"] = blog_score
        
        # 技术问答
        tech_score = 0
        for keywords_list in [self.tech_keywords, self.question_types]:
            for keywords in keywords_list.values():
                if any(keyword in user_input_lower for keyword in keywords):
                    tech_score += 1
        intent_scores["技术问答"] = tech_score
        
        # 个人咨询
        personal_keywords = ['你', '博主', '个人', '经历', '工作', '学习', '生活', '建议']
        personal_score = sum(1 for keyword in personal_keywords if keyword in user_input_lower)
        intent_scores["个人咨询"] = personal_score
        
        # 一般聊天
        chat_keywords = ['你好', '在吗', '谢谢', '再见', '早上好', '晚上好', 'hi', 'hello']
        chat_score = sum(1 for keyword in chat_keywords if keyword in user_input_lower)
        intent_scores["一般聊天"] = chat_score
        
        # 选择得分最高的意图
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]
        
        # 计算置信度
        if best_score == 0:
            confidence = 0.7  # 默认置信度
            best_intent = "技术问答"
        else:
            confidence = min(0.7 + best_score * 0.1, 0.9)
        
        # 提取槽位
        slots = self._extract_slots(user_input, best_intent)
        
        return {
            "intent": best_intent,
            "slots": slots,
            "confidence": confidence,
            "model_used": "keyword_fallback"
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

请选择适合您的方式联系，博主会尽快回复您！"""
            
            return response
        else:
            return "当前未识别到联系博主的意图。"


# 创建全局实例
_intent_recognizer: Optional[SimpleIntentRecognizer] = None

def get_intent_recognizer() -> SimpleIntentRecognizer:
    """获取意图识别器实例（单例模式）"""
    global _intent_recognizer
    if _intent_recognizer is None:
        _intent_recognizer = SimpleIntentRecognizer()
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
    'SimpleIntentRecognizer', 
    'recognize_intent', 
    'is_contact_intent', 
    'get_contact_response'
]

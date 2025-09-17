# api/ask.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from deepseek_test import ask_question  # 导入您的RAG函数

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # 调用您的RAG函数
        answer = ask_question(question)
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel需要这个变量
app = app
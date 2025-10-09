"""主入口文件 - 提供简洁的API接口"""

from modules.main import ask_question, get_completion_from_messages, initialize_system

# 导出主要功能
__all__ = ['ask_question', 'get_completion_from_messages', 'initialize_system']

# 命令行接口
if __name__ == "__main__":
    print("\n=== 文档问答系统 ===")
    initialize_system()
    
    while True:
        user_question = input("\n你的问题 (输入q退出): ")
        if user_question.lower() == 'q':
            break
            
        response = ask_question(user_question)
        print(f"\n回答: {response}")

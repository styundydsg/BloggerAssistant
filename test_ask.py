import requests
import json

def test_ask_question(question):
    """测试ask_question API"""
    url = "http://127.0.0.1:8000/ask"
    headers = {"Content-Type": "application/json"}
    data = {"question": question}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 测试问题：我的最新博客是什么
    question = "我的最新博客是什么"
    print(f"问题: {question}")
    
    result = test_ask_question(question)
    print("回答:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 判断回答是否正确
    if "answer" in result:
        answer = result["answer"]
        print(f"\n回答内容: {answer}")
        
        # 检查回答是否提到了正确的博客文件
        # 根据文件系统，最新文件是"想做游戏的第二天.md"
        if "想做游戏的第二天" in answer:
            print("✅ 回答完全正确！提到了最新的博客文件")
        elif "3月23日起床" in answer:
            print("⚠️ 回答部分正确，但可能不是最新的博客文件")
            print("   实际最新文件是: 想做游戏的第二天.md")
        elif "博客" in answer or "文章" in answer or "文档" in answer:
            print("✅ 回答看起来是合理的，提到了博客相关内容")
        else:
            print("❌ 回答可能不准确，没有提到博客相关内容")
    else:
        print("❌ API调用失败")

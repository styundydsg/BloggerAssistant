from __future__ import annotations
import pandas as pd
from openai import OpenAI
import os
import sys

import panel as pn
import langchain
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA #检索QA链，在文档上进行检索
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.evaluation.qa import QAGenerateChain
from langchain.base_language import BaseLanguageModel
from langchain.output_parsers.regex import RegexParser
from langchain.prompts import PromptTemplate
from langchain.evaluation.qa import QAEvalChain
from langchain_community.document_loaders import UnstructuredMarkdownLoader,DirectoryLoader
from langchain_community.vectorstores import FAISS

import pickle

from typing import Any
from IPython.display import display, Markdown #在jupyter显示信息的工具

langchain.debug = False

sys.path.append('../..')

pn.extension()

CONFIG = {
    "API_KEY": os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量获取
    "BASE_URL": "https://api.deepseek.com",
    "HISTORY_DIR": os.path.expanduser("~/deepseek_chat_history"),  # 跨平台路径
    "MODEL_MAPPING": {
        "V3": "deepseek-chat",
        "R1": "deepseek-reasoner"
    }
}
client = OpenAI(api_key=CONFIG["API_KEY"], base_url=CONFIG["BASE_URL"])

def get_completion_from_messages(messages, 
                                 model=CONFIG["MODEL_MAPPING"]["V3"], 
                                 temperature=0, 
                                 max_tokens=1000):
    '''

    参数: 
    messages: 这是一个消息列表，每个消息都是一个字典，包含 role(角色）和 content(内容)。角色可以是'system'、'user' 或 'assistant’，内容是角色的消息。
    model: 调用的模型，默认为 gpt-3.5-turbo(ChatGPT)，有内测资格的用户可以选择 gpt-4
    temperature: 这决定模型输出的随机程度，默认为0，表示输出将非常确定。增加温度会使输出更随机。
    max_tokens: 这决定模型输出的最大的 token 数。
    '''
    response = client.chat.completions.create(
    model=model,  # 使用传入的model参数
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
    stream=False
    )
    return response.choices[0].message.content

llm = ChatOpenAI(temperature=0,
                  model="deepseek-chat",  # 模型名称
    openai_api_key=os.getenv("DEEPSEEK_API_KEY", "sk-your-key-here"),  # DeepSeek 的 API Key
    openai_api_base="https://api.deepseek.com")  # DeepSeek 的接口地址)

delimiter = "####"

try:
    loader = DirectoryLoader(
        path='./blog_files',
        glob='**/*.md',
        loader_cls=UnstructuredMarkdownLoader,
        loader_kwargs={'encoding': 'utf-8', 'mode': 'elements'},  # 增加模式参数
        show_progress=True,
        silent_errors=True  # 忽略错误文件
    )
    data = loader.load()
    print(f"成功加载 {len(data)} 个文档片段")
except Exception as e:
    print(f"文档加载失败: {str(e)}")
    sys.exit(1)

template = """基于以下文档内容，生成一个问题及其答案：\
{doc}\
\
请严格使用以下格式：\
QUESTION: [你的问题]\
ANSWER: [对应的答案]"""


output_parser = RegexParser(
    regex=r"QUESTION:\s\*(.\*?)\s\*?ANSWER:\s\*(.\*)",  # 改进正则表达式
    output_keys=["query", "answer"]
)

PROMPT = PromptTemplate(
    input_variables=["doc"], 
    template=template, 
    output_parser=output_parser
)


class MyQAGenerateChain(QAGenerateChain):
    """自定义QA生成链"""
    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, **kwargs: Any) -> QAGenerateChain:
        return cls(llm=llm, prompt=PROMPT, **kwargs)


example_gen_chain = MyQAGenerateChain.from_llm(llm)


embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5") #初始化

vectorstore_path = "faiss_index"
if os.path.exists(vectorstore_path) and os.path.isdir(vectorstore_path):
    try:
        vectorstore = FAISS.load_local(
            vectorstore_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print("成功加载现有向量数据库")
    except:
        print("向量数据库损坏，重建中...")
        vectorstore = None
else:
    vectorstore = None

if not vectorstore:
    # 使用所有文档构建索引
    index_creator = VectorstoreIndexCreator(
        embedding=embeddings,
        vectorstore_cls=FAISS,
    )
    index = index_creator.from_documents(data)
    vectorstore = index.vectorstore
    vectorstore.save_local(vectorstore_path)
    print(f"已创建新的向量数据库，包含 {len(vectorstore.index_to_docstore_id)} 个文档")
    

qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # 返回前3个相关文档
    verbose=True,
    return_source_documents=True,  # 返回源文档
    chain_type_kwargs={
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""\
            使用以下上下文回答问题。如果你不知道答案，就说不知道。\
            \
            上下文:\
            {context}\
            \
            问题: {question}\
            答案:\
            """
        )
    }
)

def ask_question(question: str):
    """向文档提问并获取回答"""
    try:
        result = qa.invoke({"query": question})
        answer = result["result"]
        
        # 显示来源文档
        sources = "\n\n来源文档:\n" + "\n".join(
            f"- {doc.metadata['source']} (页 {doc.metadata.get('page', 'N/A')})" 
            for doc in result["source_documents"]
        )
        
        return answer + sources
    except Exception as e:
        return f"查询失败: {str(e)}"

# 8. 使用示例
if __name__ == "__main__":
    # 测试提问
    print("\n=== 文档问答系统 ===")
    while True:
        user_question = input("\n你的问题 (输入q退出): ")
        if user_question.lower() == 'q':
            break
            
        response = ask_question(user_question)
        print(f"\n回答: {response}")


# test_data = pd.read_csv(file,header=None)

# print(data[11])



# embedding_model = HuggingFaceEmbeddings(
#     model_name="BAAI/bge-large-zh-v1.5",
#     model_kwargs={"device": "cpu"},
#     encode_kwargs={"normalize_embeddings": True}
# )





# db = z.from_documents(docs, embedding=embedding_model)

# query = "Please suggest a shirt with sunblocking"

# docs = db.similarity_search(query)

# retriever = db.as_retriever()

# qdocs = "".join([docs[i].page_content for i in range(len(docs))])



# query =  "Please list all your shirts with sun protection in a table \
# in markdown and summarize each one."

# response = qa_stuff.invoke(query)

# # response = llm.call_as_llm(f"{qdocs} Question: Please list all your \
# # shirts with sun protection in a table in markdown and summarize each one.") 

# print(response)
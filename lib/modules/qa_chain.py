"""问答链模块 - 处理问答链的创建和管理"""

from typing import Any
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.base_language import BaseLanguageModel
from langchain.output_parsers.regex import RegexParser
from langchain.prompts import PromptTemplate
from langchain.evaluation.qa import QAGenerateChain

from .config import CONFIG, QA_TEMPLATE, RETRIEVAL_TEMPLATE

def create_llm() -> ChatOpenAI:
    """创建语言模型实例"""
    return ChatOpenAI(
        temperature=0,
        model="deepseek-chat",
        openai_api_key=CONFIG["API_KEY"],
        openai_api_base=CONFIG["BASE_URL"]
    )

def create_qa_chain(llm: ChatOpenAI, vectorstore) -> RetrievalQA:
    """创建问答链"""
    return RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever(search_kwargs={"k":5}),
        verbose=True,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                input_variables=["context", "question"],
                template=RETRIEVAL_TEMPLATE
            )
        }
    )

def create_qa_generate_chain(llm: BaseLanguageModel) -> QAGenerateChain:
    """创建QA生成链"""
    output_parser = RegexParser(
        regex=r"QUESTION:\s*(.*?)\s*ANSWER:\s*(.*)",
        output_keys=["query", "answer"]
    )

    prompt = PromptTemplate(
        input_variables=["doc"], 
        template=QA_TEMPLATE, 
        output_parser=output_parser
    )

    class MyQAGenerateChain(QAGenerateChain):
        """自定义QA生成链"""
        @classmethod
        def from_llm(cls, llm: BaseLanguageModel, **kwargs: Any) -> QAGenerateChain:
            return cls(llm=llm, prompt=prompt, **kwargs)

    return MyQAGenerateChain.from_llm(llm)

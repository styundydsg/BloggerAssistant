"""向量数据库管理模块 - 处理FAISS向量数据库的创建、加载和更新"""

import os
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

from .config import CONFIG
from .document_loader import load_documents



def initialize_vectorstore() -> FAISS:
    """初始化或加载向量数据库"""
    embeddings = _get_embeddings()
    
    if _vectorstore_exists():
        vectorstore = _load_existing_vectorstore(embeddings)
        _update_vectorstore_if_needed(vectorstore)
        return vectorstore
    else:
        return _create_new_vectorstore(embeddings)

def _get_embeddings() -> HuggingFaceEmbeddings:
    """获取嵌入模型"""
    return HuggingFaceEmbeddings(
        model_name=CONFIG["MODEL_DIR"],
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

def _vectorstore_exists() -> bool:
    """检查向量数据库是否存在"""
    return os.path.exists(CONFIG["VECTORSTORE_PATH"]) and os.path.isdir(CONFIG["VECTORSTORE_PATH"])

def _load_existing_vectorstore(embeddings: HuggingFaceEmbeddings) -> FAISS:
    """加载现有的向量数据库"""
    try:
        vectorstore = FAISS.load_local(
            CONFIG["VECTORSTORE_PATH"], 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print("成功加载现有向量数据库")
        return vectorstore
    except Exception:
        print("向量数据库损坏，重建中...")
        return None

def _update_vectorstore_if_needed(vectorstore: FAISS) -> None:
    """检查并更新向量数据库（如果需要）"""
    data = load_documents()
    
    existing_files = {doc.metadata['source'] for doc in vectorstore.docstore._dict.values()}
    current_files = {doc.metadata['source'] for doc in data}
    new_files = current_files - existing_files
    modified_files = set()

    # 检查修改的文件
    for doc in data:
        source = doc.metadata['source']
        if source in existing_files:
            existing_doc = next(d for d in vectorstore.docstore._dict.values() 
                               if d.metadata['source'] == source)
            if doc.metadata['last_modified'] > existing_doc.metadata.get('last_modified', 0):
                modified_files.add(source)
    
    # 如果有新文件或修改的文件，进行更新
    if new_files or modified_files:
        updated_docs = [doc for doc in data 
                       if doc.metadata['source'] in (new_files | modified_files)]
        vectorstore.add_documents(updated_docs)
        print(f"🆕 增量更新 {len(updated_docs)} 个文档片段")
        vectorstore.save_local(CONFIG["VECTORSTORE_PATH"])
    else:
        print("⏩ 未检测到文件变更，无需更新")

def _create_new_vectorstore(embeddings: HuggingFaceEmbeddings) -> FAISS:
    """创建新的向量数据库"""
    from langchain.indexes import VectorstoreIndexCreator
    
    data = load_documents()
    
    index_creator = VectorstoreIndexCreator(
        embedding=embeddings,
        vectorstore_cls=FAISS,
    )
    index = index_creator.from_documents(data)
    vectorstore = index.vectorstore
    vectorstore.save_local(CONFIG["VECTORSTORE_PATH"])
    print(f"已创建新的向量数据库，包含 {len(vectorstore.index_to_docstore_id)} 个文档")
    return vectorstore

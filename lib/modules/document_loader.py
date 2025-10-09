"""文档加载模块 - 处理Markdown文档的加载和预处理"""

import os
from typing import List, Dict
import frontmatter
from langchain_community.document_loaders import UnstructuredMarkdownLoader, DirectoryLoader
from langchain.schema import Document

from .config import CONFIG

def load_documents() -> List[Document]:
    """加载所有Markdown文档并处理元数据"""
    try:
        loader = DirectoryLoader(
            path=CONFIG["BLOG_FILES_PATH"],
            glob='**/*.md',
            loader_cls=UnstructuredMarkdownLoader,
            loader_kwargs={'encoding': 'utf-8', 'mode': 'elements'},
            show_progress=True,
            silent_errors=True,
            use_multithreading=True
        )
        data = loader.load()
        
        # 获取文件分类信息
        file_categories = _extract_categories(data)
        
        # 为每个文档片段添加元数据
        for doc in data:
            source_path = doc.metadata['source']
            doc.metadata['last_modified'] = os.path.getmtime(source_path)
            doc.metadata['file_categories'] = file_categories.get(source_path, '未分类')
        
        print(f"成功加载 {len(data)} 个文档片段")
        print(f"解析了 {len(file_categories)} 个文件的categories信息")
        return data
        
    except Exception as e:
        print(f"文档加载失败: {str(e)}")
        return []

def _extract_categories(documents: List[Document]) -> Dict[str, str]:
    """从文档中提取分类信息"""
    file_categories = {}
    
    # 获取所有唯一的md文件路径
    md_files = set()
    for doc in documents:
        source_path = doc.metadata['source']
        if source_path.endswith('.md'):
            md_files.add(source_path)
    
    # 解析每个md文件的前言部分获取categories
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            post = frontmatter.loads(content)
            categories = post.metadata.get('categories', '未分类')
            file_categories[md_file] = categories
        except Exception as e:
            print(f"解析文件 {md_file} 的前言失败: {str(e)}")
            file_categories[md_file] = '未分类'
    
    return file_categories

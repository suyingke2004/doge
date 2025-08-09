import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.tools import tool

# 加载文本嵌入模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 知识库路径
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
VECTOR_DB_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "vector_db.index")
METADATA_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "metadata.npy")

def load_vector_db():
    """加载向量数据库和元数据"""
    if not os.path.exists(VECTOR_DB_PATH) or not os.path.exists(METADATA_PATH):
        raise FileNotFoundError("未找到向量数据库或元数据文件，请先运行知识库处理脚本")
    
    # 加载向量数据库
    index = faiss.read_index(VECTOR_DB_PATH)
    
    # 加载元数据
    metadata = np.load(METADATA_PATH, allow_pickle=True)
    
    return index, metadata

@tool("Knowledge_Base_Search")
def search_knowledge_base(query: str) -> str:
    """
    根据用户问题从心理学知识库中检索相关信息。
    """
    try:
        # 加载向量数据库
        index, metadata = load_vector_db()
        
        # 将查询转换为向量
        query_vector = model.encode([query])
        
        # 归一化查询向量
        faiss.normalize_L2(query_vector)
        
        # 执行相似度搜索，获取最相关的3个文本块
        k = 3
        distances, indices = index.search(query_vector.astype('float32'), k)
        
        # 获取相关文本块
        relevant_texts = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(metadata):  # 确保索引有效
                relevant_texts.append(metadata[idx])
        
        # 将文本块拼接成一个字符串
        knowledge_context = "\n\n".join(relevant_texts)
        
        return knowledge_context
    except Exception as e:
        return f"知识库检索出错: {str(e)}"
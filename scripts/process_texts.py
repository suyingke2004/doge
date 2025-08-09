import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import glob

# 知识库路径
KNOWLEDGE_BASE_DIR = "knowledge_base"
SOURCES_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "sources")
VECTOR_DB_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "vector_db.index")
METADATA_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "metadata.npy")

# 配置镜像源以解决网络连接问题
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 模型名称和本地路径
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'local_models', MODEL_NAME)

# 加载或下载文本嵌入模型
try:
    if os.path.exists(LOCAL_MODEL_PATH):
        print(f"从本地路径加载模型: {LOCAL_MODEL_PATH}")
        model = SentenceTransformer(LOCAL_MODEL_PATH)
    else:
        print(f"本地未找到模型，正在从 Hugging Face 下载: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
        print(f"模型下载完成，正在保存到: {LOCAL_MODEL_PATH}")
        os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)
        model.save(LOCAL_MODEL_PATH)
        print("模型保存成功。")
except Exception as e:
    print(f"加载或下载模型时出错: {e}")
    print("尝试使用 TF-IDF 作为备选方案...")
    # 如果无法加载模型，使用一个简单的替代方案
    from sklearn.feature_extraction.text import TfidfVectorizer
    class SimpleModel:
        def __init__(self):
            self.vectorizer = TfidfVectorizer(max_features=384)  # 与SentenceTransformer的维度匹配
            
        def encode(self, texts):
            if isinstance(texts, str):
                texts = [texts]
            # 对于简单的TF-IDF，我们只能处理已见过的词汇
            # 这里只是一个示例，实际应用中需要更好的处理方式
            return self.vectorizer.fit_transform(texts).toarray()
    
    model = SimpleModel()

def load_texts():
    """加载所有源文本文件"""
    text_files = glob.glob(os.path.join(SOURCES_DIR, "*.txt"))
    texts = []
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            texts.append(f.read())
    return texts

def chunk_texts(texts, chunk_size=500, chunk_overlap=50):
    """将文本分割成块"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = []
    for text in texts:
        chunks.extend(text_splitter.split_text(text))
    return chunks

def embed_texts(text_chunks):
    """将文本块转换为向量"""
    embeddings = model.encode(text_chunks)
    return embeddings

def save_vector_db(embeddings, metadata):
    """保存向量数据库和元数据"""
    # 保存向量数据库
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # 使用内积相似度
    # 归一化向量
    embeddings_float32 = embeddings.astype('float32')
    faiss.normalize_L2(embeddings_float32)
    index.add(embeddings_float32)
    faiss.write_index(index, VECTOR_DB_PATH)
    
    # 保存元数据
    np.save(METADATA_PATH, metadata)

def process_knowledge_base():
    """处理知识库：加载文本、分割、向量化并保存"""
    print("正在加载文本...")
    texts = load_texts()
    if not texts:
        print("未找到源文本文件，请将文本文件放在 knowledge_base/sources 目录下")
        return
    
    print("正在分割文本...")
    chunks = chunk_texts(texts)
    print(f"共生成 {len(chunks)} 个文本块")
    
    print("正在向量化文本...")
    embeddings = embed_texts(chunks)
    print(f"向量化完成，向量维度: {embeddings.shape}")
    
    # 创建元数据
    metadata = np.array(chunks)
    
    print("正在保存向量数据库...")
    save_vector_db(embeddings, metadata)
    print("知识库处理完成！")

if __name__ == "__main__":
    process_knowledge_base()
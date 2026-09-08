# config.py
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 路径
KB_RAW_DIR = os.path.join(BASE_DIR, "kb", "ship_raw")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "kb", "chroma_ship")
COLLECTION_NAME = "ship"

# 模型
EMBEDDING_MODEL = os.path.join(BASE_DIR, "models", "bge-small-zh-v1.5")
RERANKER_MODEL = os.path.join(BASE_DIR, "models", "bge-reranker-base")
WHISPER_MODEL = "tiny"
YOLO_MODEL = os.path.join(BASE_DIR, "models", "yolov8n.pt")

# 检索参数
TOP_K_RETRIEVAL = 10
TOP_K_FINAL = 5
RERANK_ALPHA = 0.75
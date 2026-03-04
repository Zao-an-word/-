import os
import threading
from pathlib import Path

from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from typing import Tuple
import logging
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from volcenginesdkarkruntime import Ark
from chromadb import Client


# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # 数据库配置s
    DB_USER: str = "root"
    DB_PASSWORD: str = "hyx19708246637"
    DB_HOST: str = "localhost"
    DB_PORT: int =  3306
    DB_NAME: str = "text_generator"

    # JWT配置
    SECRET_KEY: str =  "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 其他配置
    DEBUG: bool = False

    @property
    def DATABASE_URL(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

# 导出配置
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

#地图生成,小说生成配置
class Config:

    #API配置 ## 使用通义千问大模型
    API_KEY: str = 'sk-df9170772565442bac1647302288355b'
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    #模型名称
    W_MODELNAME: str = "qwen-plus-latest"  # 文本处理模型
    P_MODELNAME: str = "wanx2.1-t2i-plus"  # 图像生成模型
    T_MODELNAME: str = "qwen-vl-plus"  # 视觉标注模型

    #保存目录
    OUTPUT_DIR: str = "static/output"  # 输出目录
    FONT_PATH: str = "static/simhei.ttf"  # 字体路径

    #图像配置
    IMAGE_SIZE: Tuple[int,int] = (1024, 1024)  # 图像尺寸
    FONT_SIZE_RANGE: Tuple[int,int] = (12, 36)  # 字体大小范围

class novelconfig:
    API_KEY = 'f25de5cd-62ca-4fe6-be50-4ed528169be8'
    client = Ark(api_key=API_KEY)


UPLOAD_DIR = "static/uploads"  # 保存上传文件的目录
FILE_URL= "http://localhost:8000/static/uploads"
LOCAL_FILE_DIR = Path(__file__).parent.parent.parent / "static" / "uploads"
LOCAL_FILE_DIR.mkdir(parents=True, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 确保目录存在
MAX_FILE_SIZE = 10 * 1024 * 1024
# 允许上传的文件类型（根据需求扩展）
ALLOWED_IMAGE_TYPES = {"png", "jpg", "jpeg", "gif", "bmp"}  # 支持的图片类型
ALLOWED_TEXT_TYPES = {"txt", "pdf", "docx", "doc"}  # 支持的文本类型
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_TYPES.union(ALLOWED_TEXT_TYPES)




#向量模型配置
DASHSCOPE_API_KEY = "sk-df9170772565442bac1647302288355b"
# 初始化向量数据库（Chroma）
chroma_client = Client()
collection = chroma_client.get_or_create_collection(name="multimodal_embeddings")  # 支持多模态

#     小说
# 配置封面存储路径
COVER_UPLOAD_DIR = "static/covers"
os.makedirs(COVER_UPLOAD_DIR, exist_ok=True)  # 确保目录存在

#   跨域配置
# 配置CORS
origins = [
    "http://localhost:8080",  # Vue默认端口
    "http://127.0.0.1:8080",
]

app = FastAPI(title="系统API")
# 挂载静态目录：URL 访问 /static/xxx 对应本地 static/xxx
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

#     会话
# 会话超时时间（秒）
SESSION_TIMEOUT = 60
# 存储会话ID到端口的映射关系
session_port_map = {}
# 存储端口占用状态（True表示已占用，False表示可用）
port_status = {}
# 存储会话最后活跃时间（用于超时管理）
session_last_active = {}


lock = threading.Lock()

logger.info(f"CORS 配置已加载，允许的源: {origins}")

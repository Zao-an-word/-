from http import HTTPStatus
from pathlib import Path
import base64
from dashscope import MultiModalEmbedding  # 阿里云多模态嵌入模型
from openai import OpenAI

from ..core.config import DASHSCOPE_API_KEY, collection

# 验证dashscope密钥
if not DASHSCOPE_API_KEY:
    raise ValueError("请在.env文件中配置DASHSCOPE_API_KEY（阿里云灵积平台密钥）")

# 初始化OpenAI客户端（兼容阿里百炼）
client = OpenAI(
    # 使用环境变量或直接设置API密钥
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# def get_image_description(image_path: Path) -> str:
#     """临时方案：跳过 OCR，直接返回图片格式信息"""
#     try:
#         from PIL import Image
#         # 仅获取图片基本信息（尺寸、格式），不做文字提取
#         with Image.open(image_path) as img:
#             width, height = img.size
#             return f"图片文件（格式：{image_path.suffix}，尺寸：{width}x{height}像素）"
#     except Exception as e:
#         return f"图片信息获取失败：{str(e)}"

def get_image_description(image_path: Path) -> str:
    """增强版：获取图片基本信息 + 调用qwen-vl-plus进行AI图片理解"""
    try:
        from PIL import Image

        # 1. 获取图片基本信息（尺寸、格式）
        with Image.open(image_path) as img:
            width, height = img.size
            basic_info = f"图片文件（格式：{image_path.suffix}，尺寸：{width}x{height}像素）"

        # 2. 将本地图片转换为Base64格式（用于传递给AI模型）
        try:
            with open(image_path, "rb") as image_file:
                # 转换为Base64编码
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                # 构建符合要求的图片URL格式
                image_url = f"data:image/{image_path.suffix.lstrip('.')};base64,{base64_image}"
        except Exception as e:
            return f"{basic_info}。图片编码失败：{str(e)}"

        # 3. 调用qwen-vl-plus模型进行图片理解
        try:
            completion = client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url}},
                            {"type": "text", "text": "请详细描述这张图片的内容，包括主要物体、场景、颜色和可能的主题。"}
                        ]
                    }
                ]
            )

            # 提取AI生成的描述
            ai_description = completion.choices[0].message.content
            return f"{basic_info}\nAI图片分析：{ai_description}"

        except Exception as ai_err:
            # AI分析失败时仍返回基本信息
            return f"{basic_info}。AI图片分析失败：{str(ai_err)}"

    except Exception as e:
        return f"图片信息获取失败：{str(e)}"

async def process_and_store_text(text: str, file_id: str, is_image: bool = False):
    """处理文本/图片并存储向量"""
    if is_image:
        await _process_image(text, file_id)  # text此时为本地图片路径
    else:
        await _process_text(text, file_id)
    return {"status": "success", "file_id": file_id}


async def _process_image(local_image_path: str, file_id: str):
    """处理图片：读取本地文件→转换为Base64→生成向量→存储（含描述）"""
    image_path = Path(local_image_path)
    if not image_path.exists():
        raise ValueError(f"本地图片文件不存在：{local_image_path}")

    # 1. 生成图片文本描述（新增）
    image_desc = get_image_description(image_path)  # 调用新增的描述函数

    # 2. 图片转换为Base64（保持不变）
    try:
        with open(image_path, "rb") as f:
            base64_str = base64.b64encode(f.read()).decode("utf-8").replace("\n", "")
        file_ext = image_path.suffix.lower().lstrip(".")
        image_data = f"data:image/{file_ext};base64,{base64_str}"
    except Exception as e:
        raise ValueError(f"图片Base64转换失败：{str(e)}")

    # 3. 生成向量（保持不变）
    input_data = [{"image": image_data}]
    try:
        resp = MultiModalEmbedding.call(
            model="multimodal-embedding-v1",
            input=input_data,
            api_key=DASHSCOPE_API_KEY
        )
        if resp.status_code != HTTPStatus.OK:
            raise Exception(f"图片向量生成失败：{resp.message}（code:{resp.code}）")
        image_embedding = resp.output["embeddings"][0]["embedding"]
    except Exception as e:
        raise ValueError(f"图片向量生成失败：{str(e)}")

    # 4. 存储向量（关键修改：documents存入图片描述）
    collection.add(
        ids=[f"{file_id}_image"],
        documents=[image_desc],  # 存储图片描述（替代原有的"图片文件：{file_id}"）
        embeddings=[image_embedding],
        metadatas=[{
            "file_id": file_id,
            "type": "image",
            "local_path": str(image_path),
            "description": image_desc  # 元数据也保留描述，便于调试
        }]
    )


# 文本处理函数（保持不变）
async def _process_text(text: str, file_id: str):
    """处理纯文本：分块→生成向量→存储"""
    if not text.strip():
        raise ValueError("文件解析后无有效文本内容")

    # 1. 文本分块
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # 确保导入
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    print(f"文本分块完成：{file_id}，共{len(chunks)}块")

    # 2. 调用dashscope生成文本向量
    embeddings = []
    for i, chunk in enumerate(chunks):
        input_data = [{"text": chunk}]
        try:
            resp = MultiModalEmbedding.call(
                model="multimodal-embedding-v1",
                input=input_data,
                api_key=DASHSCOPE_API_KEY
            )
            if resp.status_code == HTTPStatus.OK:
                text_embedding = resp.output["embeddings"][0]["embedding"]
                embeddings.append(text_embedding)
                print(f"文本块{i}向量生成成功，维度：{len(text_embedding)}")
            else:
                raise Exception(f"dashscope调用失败：{resp.message}（code:{resp.code}）")
        except Exception as e:
            raise ValueError(f"文本块{i}向量生成失败：{str(e)}")

    # 3. 存储到向量数据库
    chunk_ids = [f"{file_id}_text_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"file_id": file_id, "type": "text", "chunk_index": i} for i in range(len(chunks))]
    collection.add(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
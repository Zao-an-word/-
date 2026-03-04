from http import HTTPStatus
from typing import Optional, List
import dashscope
from langchain.chains import LLMChain

from dashscope import  Generation
from ..core.config import DASHSCOPE_API_KEY

dashscope.api_key = DASHSCOPE_API_KEY




async def generate_question_embedding(question: str) -> Optional[List[float]]:
    """生成问题的向量表示"""
    try:
        input_data = [{"text": question}]
        resp = dashscope.MultiModalEmbedding.call(
            model="multimodal-embedding-v1",
            input=input_data
        )

        if resp.status_code == HTTPStatus.OK:
            return resp.output["embeddings"][0]["embedding"]
        else:
            raise Exception(f"生成向量失败: {resp.message}")
    except Exception as e:
        print(f"向量生成错误: {str(e)}")
        return None


async def generate_answer(question: str, retrieved_docs: List[dict]) -> str:
    """调用大模型，结合检索到的文档生成回答"""
    # 构建提示词
    prompt = f"""请根据以下提供的参考文档，回答用户的问题。
如果参考文档中没有相关信息，请直接说明"没有找到相关信息"。
回答要简洁明了，基于参考文档内容，不要添加额外信息。

参考文档:
{chr(10).join([doc['content'] for doc in retrieved_docs])}

用户问题: {question}
回答:
"""

    # 调用大模型
    try:
        response = Generation.call(
            model="qwen-plus-latest",  # 可替换为其他模型
            prompt=prompt,
            temperature=0.3,  # 控制回答随机性，0.3表示较确定
            top_p=0.8
        )

        if response.status_code == HTTPStatus.OK:
            return response.output["text"].strip()
        else:
            return f"生成回答失败: {response.message}"
    except Exception as e:
        return f"调用大模型出错: {str(e)}"
from http import HTTPStatus
from pathlib import Path
from typing import List, Optional
from ....services.query_service import  generate_question_embedding, generate_answer
from typing import List
from ....core.config import logger, COVER_UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, UPLOAD_DIR, novelconfig, \
    ALLOWED_IMAGE_TYPES, ALLOWED_TEXT_TYPES, FILE_URL, LOCAL_FILE_DIR
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form, Body
from pydantic import BaseModel
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from starlette.responses import JSONResponse
import uuid  # 用于生成唯一文件名
from langchain.chains import RetrievalQAWithSourcesChain

from ....services.auth_service import (
    allowed_file,
    save_file,
    get_image_preview,
    extract_text
)
from ....services.text_service import process_and_store_text, collection

# 初始化 FastAPI 应用
router = APIRouter()

# 数据模型（请求/响应格式）
class QueryRequest(BaseModel):
    question: str
    file_ids: Optional[List[str]] = None  # 关联的文件ID列表
    top_k: int = 3

class UploadResponse(BaseModel):
    file_id: str
    message: str

class QueryResponse(BaseModel):
    answer: str


@router.post("/upload-files", response_class=JSONResponse)
async def upload_files(
        files: List[UploadFile] = File(
            ..., description="支持上传图片（png/jpg等）和文本（txt/pdf/docx等）"
        ),
        chat_id: Optional[str] = Form(None, description="关联的对话ID")
):
    results = []

    # 校验本地存储路径
    if not isinstance(LOCAL_FILE_DIR, Path) or not LOCAL_FILE_DIR.exists():
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="文件存储路径配置错误，请检查LOCAL_FILE_DIR"
        )

    for file in files:
        file_result = {
            "filename": file.filename or "unknown",
            "status": "pending",
            "file_id": None,
            "reason": None
        }
        try:
            filename = file.filename or "unknown"
            file_ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

            # 大小和类型校验
            if file.size and file.size > MAX_FILE_SIZE * 3 / 10:
                raise HTTPException(
                    status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    detail=f"图片文件过大（最大支持{MAX_FILE_SIZE*3/10 / 1024 / 1024:.2f}MB）"
                )
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"不支持的类型（允许：{sorted(ALLOWED_EXTENSIONS)}）"
                )

            # 生成唯一标识和本地存储路径
            file_id = str(uuid.uuid4())
            save_path = LOCAL_FILE_DIR / f"{file_id}_{filename}"

            # 保存文件到本地服务器
            await save_file(file, save_path)

            # 生成前端访问URL（仅用于前端预览，向量生成不再使用）
            file_url = f"{FILE_URL}/{save_path.name}"
            is_image = file_ext in ALLOWED_IMAGE_TYPES

            file_info = {
                "filename": filename,
                "file_id": file_id,
                "file_ext": file_ext,
                "file_url": file_url,  # 前端访问用URL
                "chat_id": chat_id,
                "is_image": is_image
            }

            # 图片处理（核心修改：使用Base64编码生成向量）
            if is_image:
                try:
                    # 生成预览图（保持不变）
                    preview = get_image_preview(save_path)
                    if preview:
                        file_info["preview_base64"] = preview
                except Exception as e:
                    file_info["warning"] = f"预览生成失败：{str(e)}"

                # 调用处理函数（传递本地路径，而非URL）
                await process_and_store_text(
                    text=str(save_path),  # 改为传递本地文件路径
                    file_id=file_id,
                    is_image=True
                )
                file_info["message"] = "图片上传并生成向量成功"

            # 文本处理（保持不变）
            else:
                try:
                    text_content = extract_text(save_path, file_ext)
                    file_info["text_preview"] = text_content[:200]
                except Exception as e:
                    raise ValueError(f"文本提取失败：{str(e)}")

                await process_and_store_text(
                    text=text_content,
                    file_id=file_id,
                    is_image=False
                )
                file_info["message"] = "文本上传并生成向量成功"

            file_result.update({
                "status": "success",
                "file_id": file_id,
                "detail": file_info
            })

        except HTTPException as e:
            file_result["status"] = "failed"
            file_result["reason"] = e.detail
        except Exception as e:
            file_result["status"] = "failed"
            file_result["reason"] = f"处理失败：{str(e)}"
        finally:
            await file.close()
            results.append(file_result)

    success_count = sum(1 for r in results if r["status"] == "success")
    return {
        "message": f"处理完成，成功上传 {success_count}/{len(files)} 个文件",
        "results": results
    }


# @router.post("/query", response_model=QueryResponse)
# async def query_endpoint(request: QueryRequest):
#     """问答接口：接收问题和文件ID，返回AI回答"""
#     try:
#         answer = await handle_query(request.question, request.file_ids)
#         return {"answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"问答失败：{str(e)}")

@router.post("/query", response_class=JSONResponse)
async def query(req: QueryRequest = Body(...)):
    try:
        # 1. 生成问题向量
        question_embedding = await generate_question_embedding(req.question)
        if not question_embedding:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="生成问题向量失败"
            )

        # 2. 从向量数据库检索相关文档（移除 filter 参数）
        # 旧版本 Chromadb 不支持 filter，先查询所有结果
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=req.top_k
        )

        # 3. 后处理：按 file_ids 筛选结果
        retrieved_docs = []
        if "documents" in results and len(results["documents"][0]) > 0:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                # 如果指定了 file_ids，只保留匹配的文档
                if req.file_ids and len(req.file_ids) > 0:
                    # 检查当前文档的 file_id 是否在请求的 file_ids 中
                    if meta.get("file_id") not in req.file_ids:
                        continue  # 不匹配则跳过
                # 保留符合条件的文档
                retrieved_docs.append({
                    "content": doc,
                    "type": meta.get("type", "unknown"),
                    "file_id": meta.get("file_id", ""),
                    "chunk_index": meta.get("chunk_index", -1)
                })

        # 4. 调用大模型生成回答
        answer = await generate_answer(req.question, retrieved_docs)

        return {
            "status": "success",
            "question": req.question,
            "answer": answer,
            "related_docs": retrieved_docs,
            "count": len(retrieved_docs)
        }

    except Exception as e:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"查询失败: {str(e)}",
                "details": str(e)
            }
        )

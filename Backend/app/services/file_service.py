import os
import uuid
from fastapi import UploadFile
from ..core.config import  LOCAL_FILE_DIR  # 建议从配置文件导入绝对路径
from ..services.file_utils import parse_file
from ..services.text_service import process_and_store_text


TEMP_DIR =  LOCAL_FILE_DIR
TEMP_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在


async def upload_file(file: UploadFile) -> str:
    temp_path = None  # 初始化temp_path为None
    try:
        file_id = str(uuid.uuid4())
        # 拼接临时文件路径（绝对路径）
        temp_path = TEMP_DIR / f"{file_id}_{file.filename}"

        # 异步读取并保存文件

        with open(temp_path, "wb") as f:
            f.write(await file.read())  # 正确的异步读取

        # 解析文件内容
        text_content = parse_file(temp_path, file.filename)

        # 处理文本（调用异步函数，正确使用await）
        await process_and_store_text(text_content, file_id)

        return file_id

    finally:
        # 清理临时文件（检查temp_path是否有效）
        if temp_path is not None and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"临时文件已删除：{temp_path}")
            except OSError as e:
                print(f"删除临时文件失败：{e}")  # 仅警告，不中断流程
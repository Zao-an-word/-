from pathlib import Path
import PyPDF2
from docx import Document
import pandas as pd

def parse_file(file_path: Path, filename: str) -> str:
    """根据文件扩展名调用对应的解析函数"""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return _parse_docx(file_path)
    elif ext in [".xlsx", ".xls", ".csv"]:
        return _parse_excel(file_path, ext)
    elif ext in [".txt", ".md"]:
        return _parse_text(file_path)
    else:
        raise ValueError(f"不支持的文件类型：{ext}")

def _parse_pdf(file_path: Path) -> str:
    """解析 PDF 文件文本"""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def _parse_docx(file_path: Path) -> str:
    """解析 Word 文件文本"""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def _parse_excel(file_path: Path, ext: str) -> str:
    """解析 Excel/CSV 文件文本（转换为描述性文本）"""
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    # 将表格转换为 "行-列-值" 描述（方便大模型理解）
    text = f"表格名称：{file_path.name}\n"
    text += f"列名：{', '.join(df.columns)}\n"
    text += "表格内容：\n"
    for idx, row in df.iterrows():
        text += f"第{idx+1}行：{row.to_dict()}\n"
    return text

def _parse_text(file_path: Path) -> str:
    """解析纯文本文件"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
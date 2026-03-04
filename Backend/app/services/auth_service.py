from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytz
from ..core.config import SECRET_KEY, ALGORITHM
from ..db.session import get_db
from ..domains.users.models import User
from ..domains.users.schemas import UserCreate,UserProfileUpdate
from ..core.security import get_password_hash, verify_password
from ..domains.novels.models import Novels
import logging
from ..core.config import  novelconfig,Config,ALLOWED_EXTENSIONS
from http import HTTPStatus
import json
import re
import requests
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from typing import  Dict, Any
from openai import OpenAI, OpenAIError
from dashscope import ImageSynthesis
from PIL import  ImageDraw, ImageFont
from jose import jwt, JWTError
import os
import base64
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import uuid
import fitz  # 处理PDF（pip install pymupdf）
import docx  # 处理docx（pip install python-docx）
from PIL import Image  # 处理图片（pip install pillow）
import io

logger = logging.getLogger(__name__)

# 获取用户
async def get_user_by_username(db: AsyncSession, username: str):
    try:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error retrieving user by username {username}: {e}")
        raise

# 创建用户
async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        phone=user.phone,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        status=0  # 0表示离线
    )
    db.add(db_user)
    await db.commit()  # 异步提交
    await db.refresh(db_user)  # 异步刷新
    return db_user

# 更新用户个人信息
async def update_user_profile(db: AsyncSession, user: User, profile_update: UserProfileUpdate):
    update_data = profile_update.dict(exclude_unset=True)  # 只更新提供的字段
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

# 验证用户
async def authenticate_user(db: AsyncSession, username: str, password: str):
    try:
        user = await get_user_by_username(db, username)
        if not user:
            return False
        if not verify_password(password, user.password_hash):
            return False
        return user
    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}")
        raise

# 异步（正确）
async def get_online_users_count(db: AsyncSession):
    try:
        threshold = datetime.now(pytz.utc) - timedelta(minutes=30)
        result = await db.execute(
            select(func.count()).where(
                User.last_login_at >= threshold,
                User.status == 1
            )
        )
        return result.scalar()
    except Exception as e:
        logger.error(f"Error getting online users count: {e}")
        raise

# 异步（正确）
async def get_total_users_count(db: AsyncSession):
    try:
        result = await db.execute(select(func.count()).select_from(User))
        return result.scalar()
    except Exception as e:
        logger.error(f"Error getting total users count: {e}")
        raise

# 异步（正确）
async def get_usage_peak_hours(db: AsyncSession):
    try:
        threshold = datetime.now(pytz.utc) - timedelta(days=7)
        subquery = (
            select(
                func.extract('hour', User.last_login_at).label('hour'),
                func.count().label('count')
            ).filter(
                User.last_login_at >= threshold
            ).group_by(
                func.extract('hour', User.last_login_at)
            ).subquery()
        )
        result = await db.execute(
            select(
                subquery.c.hour,
                subquery.c.count
            ).order_by(
                subquery.c.count.desc()
            ).limit(3)
        )
        peak_hours = result.all()
        return [{"hour": int(hour), "count": count} for hour, count in peak_hours]
    except Exception as e:
        logger.error(f"Error getting usage peak hours: {e}")
        raise

# 异步（正确）
async def get_current_active_user(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/login")),
        db: AsyncSession = Depends(get_db)  # 依赖异步会话
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user = await get_user_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        if user.status != 1:
            raise HTTPException(status_code=400, detail="非活跃用户")
        return user
    except Exception as e:
        logger.error(f"Error getting current active user {username}: {e}")
        raise


# 获取所有小说信息，包含作者名
async def get_all_novels_with_author(db: AsyncSession):
    query = select(Novels, User.username.label("author_name")).join(User, Novels.user_id == User.id)
    result = await db.execute(query)

    novels_data = []
    for novel, author_name in result:
        novels_data.append({
            "id": novel.id,
            "author_name": author_name,
            "title": novel.title,
            "content": novel.content,
            "introduction": novel.introduction,
            "tags": novel.tags,  # ✅ 加上标签
            "cover_url": novel.cover_url,
            "created_at": novel.created_at,
            "updated_at": novel.updated_at
        })
    return novels_data

def generate_novel_introduction(text:str=None):

    try:
        # 初始化AI配置
        novel_c = novelconfig()
        # 调用AI接口生成内容
        completion = novel_c.client.chat.completions.create(
            model="doubao-seed-1-6-thinking-250715",
            messages=[
                {"role": "system", "content": f"""
                    你是一名编辑，可以对小说进行精确概括
                    用尽量简短但是吸引人的文字来概述小说
                    小说内容为{text}
                """},
            ]
        )

        # 提取并返回生成的内容
        return completion.choices[0].message.content.strip()

    except Exception as e:
        # 捕获AI调用过程中的所有异常
        raise Exception(f"AI生成小说概括失败: {str(e)}")

class MapGenerator:
    """地图生成器"""

    def __init__(self, config: Config = Config()):
        self.config = config  # 接收配置实例
        self.logger = self._init_logger()
        self._init_output_dir()
        self.openai_client = OpenAI(
            api_key=self.config.API_KEY,
            base_url=self.config.BASE_URL
        )

    def _init_logger(self) -> logging.Logger:
        """初始化日志系统"""
        logger = logging.getLogger("map_generator")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _init_output_dir(self) -> None:
        """初始化输出目录"""
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        self.logger.info(f"输出目录已初始化：{self.config.OUTPUT_DIR}")

    def generate_map_prompt(self, text: str) -> str:
        """生成地图描述文本"""
        self.logger.info("开始生成地图描述...")
        try:
            completion = self.openai_client.chat.completions.create(
                model=self.config.W_MODELNAME,
                messages=[{"role": "system", "content": self._get_system_prompt()},{"role": "user", "content": text}]
            )
            return completion.choices[0].message.content
        except OpenAIError as e:
            self.logger.error(f"地图描述生成失败：{str(e)}")
            raise Exception(f"地图描述生成失败：{str(e)}")

    def _get_system_prompt(self) -> str:
        """地图描述生成的系统提示词"""
        return  """
你是一位熟悉小说世界构造的地图绘制专家，任务是根据小说片段生成一个结构化的“文字版地图描述”。请严格遵循以下步骤和输出格式：

【提取要素】
1. 提取所有出现的地点（城镇、村庄、山脉、河流等），说明是否为主要地点。
2. 分析地点之间的相对位置、方位关系、距离（如“在X东边百里”）。
3. 判断层级关系（如“某王国包含多个城市”）与特殊空间规则（如“迷雾无法通行”）。
4. 将模糊描述量化：如“半天路程”可换算为100公里（或200像素）。

【输出格式要求】
请严格使用以下结构，坐标值范围在 (0~1024)：
地图标题（如：“北境领地全景图”）(x=512, y=0)
整体范围：y<200为北境高原，y>900为南方密林
核心地点及位置：
- 冰封城：位于(512,512)，是主要城市，西距寒霜堡(300,512)约40公里
- 寒霜堡：位于(300,512)，为边境要塞，东距冰封城约40公里
- 黑森林：自(200,700)延伸至(600,1024)，为危险地带
地形与路线：
- 寒霜山脉横贯(100,200)至(900,400)，仅北口隘道(450,300)可通行
视觉标注说明：
- 主要城市：红色城堡图标；村庄：蓝色小屋；危险区域：灰色阴影覆盖
特殊说明：
- 黑森林区域存在幻境，地图上标为“迷失区”，具体结构不明

【禁止行为】
- 不要输出中间思考过程。
- 不要生成自然语言分析性内容。
- 严格使用结构化段落格式。

请基于小说内容完成上述结构的地图文字描述。
"""

    def generate_base_map(self, map_prompt: str) -> str:
        """生成基础无字地图"""
        self.logger.info("开始生成基础无字地图...")
        try:
            prompt = f"""
            根据以下地图描述，生成一张无任何文字符号的堪舆图:
            "{map_prompt}"
            要求如下：
            1.严格按照文字版地图描述
            2.不同区域用不同颜色表示
            3.禁用所有文字、数字、符号
            4.强调图形关系，不依赖文字说明
            5.图像中不得出现可读性内容
            6.检查每个地点与地图的匹配度，如果出现极大偏差则重新生成
            6.将图像与原文进行匹配，若匹配度低于80%，重新生成
            """
            rsp = ImageSynthesis.call(
                api_key=self.config.API_KEY,
                model=self.config.P_MODELNAME,
                prompt=prompt,
                n=1,
                size=f'{self.config.IMAGE_SIZE[0]}*{self.config.IMAGE_SIZE[1]}'
            )
            if rsp.status_code != HTTPStatus.OK:
                raise Exception(f"图像生成失败：{rsp.code} - {rsp.message}")

            # 保存基础地图
            url = rsp.output.results[0].url
            file_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
            image_path = os.path.join(self.config.OUTPUT_DIR, file_name)

            with open(image_path, 'wb+') as f:
                f.write(requests.get(url).content)

            self.logger.info(f"基础地图已保存：{image_path}")
            return image_path
        except Exception as e:
            self.logger.error(f"基础地图生成失败：{str(e)}")
            raise Exception(f"基础地图生成失败：{str(e)}")

    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_str = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded_str}"
        except Exception as e:
            self.logger.error(f"图片编码失败：{str(e)}")
            raise Exception(f"图片编码失败：{str(e)}")

    def get_annotation_instructions(self, image_data_uri: str, text: str) -> List[Dict[str, Any]]:
        """获取地图标注指令"""
        self.logger.info("开始获取标注指令...")
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_data_uri}},
                        {"type": "text", "text": (
                            "【任务目标】：根据地图图像和文字描述生成地名标注坐标信息。\n"
                            "【地图规格】：尺寸为1024x1024，无文字，仅包含不同区域颜色区分。\n"
                            "【输出要求】：\n"
                            "- 每个地点为一个 JSON 对象，字段为：text，position[x, y]，color（统一为black），font_size。\n"
                            "- font_size 范围为 18~48。\n"
                            "- text 值必须是原文中已出现的地点名称。\n"
                            "- 严格输出为 JSON 数组，不包含代码块标记或解释性语言。\n"
                            "【原始描述】：以下是基于文本生成的地图描述，请根据它提取标注信息：\n"
                            f"{text}"
                        )}
                    ]
                }
            ]
            completion = self.openai_client.chat.completions.create(
                model=self.config.T_MODELNAME,
                messages=messages
            )
            raw_response = completion.choices[0].message.content.strip()
            cleaned_response = self._clean_json_response(raw_response)
            return json.loads(cleaned_response)
        except (OpenAIError, json.JSONDecodeError) as e:
            self.logger.error(f"标注指令获取失败：{str(e)}")
            raise Exception(f"标注指令获取失败：{str(e)}")

    def _clean_json_response(self, response: str) -> str:
        """清理API返回的JSON响应"""
        response = response.strip()
        # 移除代码块标记
        if response.startswith("```json"):
            response = response[len("```json"):].strip()
        elif response.startswith("```"):
            response = response.split("\n", 1)[-1].strip()
        if response.endswith("```"):
            response = response.rsplit("```", 1)[0].strip()

        # 提取JSON核心部分
        start_idx = response.find("[")
        end_idx = response.rfind("]") + 1
        if start_idx == -1 or end_idx <= start_idx:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
        if start_idx != -1 and end_idx > start_idx:
            response = response[start_idx:end_idx]

        # 修复坐标格式
        response = re.sub(r'\((\d+)\s*,\s*(\d+)\)', r'[\1, \2]', response)
        return response

    def annotate_map(self, image_path: str, instructions: List[Dict[str, Any]]) -> str:
        """为地图添加文字标注"""
        self.logger.info("开始标注地图...")
        try:
            # 生成最终输出路径
            final_output_path = os.path.join(
                self.config.OUTPUT_DIR,
                f"{uuid.uuid4()}_final.png"
            )

            # 打开图片并绘制标注
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            for item in instructions:
                text = item.get("text")
                position = tuple(item.get("position", (100, 100)))
                font_size = item.get("font_size", 24)
                color = item.get("color", "black")

                # 限制字体大小在配置范围内
                font_size = max(
                    self.config.FONT_SIZE_RANGE[0],
                    min(font_size, self.config.FONT_SIZE_RANGE[1])
                )

                # 加载字体
                try:
                    font = ImageFont.truetype(self.config.FONT_PATH, font_size)
                except Exception:
                    self.logger.warning("无法加载指定字体，使用默认字体")
                    font = ImageFont.load_default()

                draw.text(position, text, fill=color, font=font)

            image.save(final_output_path)
            self.logger.info(f"标注完成，地图保存至：{final_output_path}")
            return final_output_path
        except Exception as e:
            self.logger.error(f"地图标注失败：{str(e)}")
            raise Exception(f"地图标注失败：{str(e)}")

    async def generate_map(self, text: str) -> str:
        try:
            map_prompt = self.generate_map_prompt(text)  # OpenAI 同步调用，也可改 async
            self.logger.info(f"地图生成提示词内容如下：\n{map_prompt}")  # ✅ 关键行，输出地图提示词

            base_map_path = self.generate_base_map(map_prompt)  # 可改 async
            image_data_uri = self.encode_image_to_base64(base_map_path)
            instructions = self.get_annotation_instructions(image_data_uri, map_prompt)  # 改为 async
            final_map_path = self.annotate_map(base_map_path, instructions)

            relative_path = os.path.relpath(final_map_path, self.config.OUTPUT_DIR).replace("\\", "/")
            return f"/output/{relative_path}"
        except Exception as e:
            self.logger.error(f"地图生成失败：{str(e)}")
            raise

#                                              文件上传
#333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333


# 检查文件类型是否允许
def allowed_file(filename: str) -> bool:
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 保存文件到本地
async def save_file(file: UploadFile, save_path: str):
    with open(save_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):  # 分块读取（1MB/块）
            buffer.write(content)


# 提取文本文件内容（支持txt、pdf、docx）
def extract_text(file_path: str, file_ext: str) -> Optional[str]:
    try:
        if file_ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(10000)  # 限制最大读取长度（避免过大）

        elif file_ext == "pdf":
            doc = fitz.open(file_path)
            text = []
            for page in doc:
                text.append(page.get_text())
            return "\n".join(text)[:10000]

        elif file_ext in ["docx", "doc"]:
            doc = docx.Document(file_path)
            text = [para.text for para in doc.paragraphs]
            return "\n".join(text)[:10000]

        else:
            return None
    except Exception as e:
        print(f"提取文本失败：{str(e)}")
        return f"文件内容提取失败：{str(e)}"


# 生成图片Base64预览（小尺寸）
def get_image_preview(file_path: str) -> Optional[str]:
    try:
        with Image.open(file_path) as img:
            # 压缩图片尺寸（最长边不超过200px）
            img.thumbnail((200, 200))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"生成图片预览失败：{str(e)}")
        return None



from enum import Enum
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime,date
from typing import Optional


# 用户登录响应模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 用户创建请求模型
class UserCreate(BaseModel):
    username: str
    password: str = Field(...,min_length=6,description="密码长度至少6位")
    phone: Optional[str] = None
    nickname: Optional[str] = ""
    avatar_url: Optional[str] = ""

    class Config:
        from_attributes = True


# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: str
    status: int
    role: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    phone_verified: bool
    remark: Optional[str] = None
    birthday: date | None = Field(None, description="生日可为空")
    gender: str | None = None
    mailbox: str | None = None
    class Config:
        from_attributes = True

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = '@/assets/img/userProfile.jpg'
    remark: Optional[str] = None
    gender: Optional[Gender] = Gender.male  # 使用枚举类型
    birthday: Optional[date] = None
    mailbox: Optional[EmailStr] = None  # 使用EmailStr类型

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str
    role: int

# 管理员统计信息模型
class AdminStats(BaseModel):
    online_users_count: int
    total_users_count: int
    usage_peak_hours: list

# 定义请求体模型
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码，至少6位")

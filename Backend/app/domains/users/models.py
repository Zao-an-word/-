# app/domains/users/models.py

from ...db.base import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func,Date
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"

    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), nullable=False, index=True, comment="用户名")
    password_hash = Column(String(128), nullable=False, comment="密码哈希值")
    phone = Column(String(20), nullable=True, comment="手机号")
    nickname = Column(String(64), default='', comment="昵称")
    avatar_url = Column(String(255), default='', comment="头像URL")
    status = Column(Integer, default=2, comment="用户状态")
    role = Column(Integer, default=0, comment="用户角色")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    phone_verified = Column(Boolean, default=False, comment="手机号验证状态")
    remark = Column(String(255), default='', comment="备注信息")
    birthday = Column(Date,nullable = True,server_default=func.now(),comment = '生日')
    gender = Column(String(20),default="male",comment='性别')
    mailbox = Column(String(45),default='',comment='邮箱')

    conversations = relationship("Conversations", back_populates="user")
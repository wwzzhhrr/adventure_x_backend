from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UserCreate(BaseModel):
    """用户注册请求模型"""
    email: EmailStr
    username: str
    password: str
    bio: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr
    password: str

class UserUpdateBio(BaseModel):
    """用户更新bio请求模型"""
    bio: Optional[str] = None

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    email: str
    username: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class Token(BaseModel):
    """JWT令牌响应模型"""
    access_token: str
    token_type: str
    user: UserResponse

class TaskCreate(BaseModel):
    """任务创建请求模型"""
    title: str
    description: Optional[str] = None
    reward_amount: Optional[Decimal] = None
    skill_tags: Optional[List[str]] = None

class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    title: str
    description: Optional[str] = None
    creator_id: int
    reward_amount: Optional[Decimal] = None
    status: str
    skill_tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
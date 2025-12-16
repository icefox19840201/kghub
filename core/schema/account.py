"""
账户相关的Pydantic模型
基于SQLAlchemy ORM模型结构
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description='用户名或邮箱', min_length=1, max_length=100)
    password: str = Field(..., description='账户密码', min_length=1, max_length=128)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., description='用户名', min_length=3, max_length=50)
    email: EmailStr = Field(..., description='邮箱地址')
    password: str = Field(..., description='密码', min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, description='全名', max_length=100)
    phone: Optional[str] = Field(None, description='手机号', max_length=20)
    avatar: Optional[str] = Field(None, description='头像URL', max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "phone": "13800138000",
                "avatar": "https://example.com/avatar.jpg"
            }
        }


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = Field(None, description='邮箱地址')
    full_name: Optional[str] = Field(None, description='全名', max_length=100)
    phone: Optional[str] = Field(None, description='手机号', max_length=20)
    avatar: Optional[str] = Field(None, description='头像URL', max_length=255)
    is_active: Optional[bool] = Field(None, description='是否激活')
    is_superuser: Optional[bool] = Field(None, description='是否超级管理员')
    is_staff: Optional[bool] = Field(None, description='是否员工')
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "John Smith",
                "phone": "13900139000",
                "is_active": True
            }
        }


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description='用户ID')
    username: str = Field(..., description='用户名')
    email: str = Field(..., description='邮箱地址')
    full_name: Optional[str] = Field(None, description='全名')
    phone: Optional[str] = Field(None, description='手机号')
    avatar: Optional[str] = Field(None, description='头像URL')
    is_active: bool = Field(..., description='是否激活')
    is_superuser: bool = Field(..., description='是否超级管理员')
    is_staff: bool = Field(..., description='是否员工')
    date_joined: datetime = Field(..., description='注册时间')
    last_login: Optional[datetime] = Field(None, description='最后登录时间')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Administrator",
                "phone": "13800138000",
                "avatar": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_superuser": True,
                "is_staff": True,
                "date_joined": "2024-01-01T00:00:00",
                "last_login": "2024-01-15T12:30:00",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-15T12:30:00"
            }
        }


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int = Field(..., description='总用户数')
    users: list[UserResponse] = Field(..., description='用户列表')
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "users": [
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "full_name": "Administrator",
                        "is_active": True,
                        "is_superuser": True,
                        "date_joined": "2024-01-01T00:00:00"
                    }
                ]
            }
        }


class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str = Field(..., description='旧密码', min_length=6, max_length=128)
    new_password: str = Field(..., description='新密码', min_length=6, max_length=128)
    confirm_password: str = Field(..., description='确认新密码', min_length=6, max_length=128)
    
    def validate_passwords_match(self):
        """验证新密码和确认密码是否匹配"""
        if self.new_password != self.confirm_password:
            raise ValueError('新密码和确认密码不匹配')
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


class PasswordReset(BaseModel):
    """密码重置模型"""
    email: EmailStr = Field(..., description='注册邮箱')
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }



"""
ORM Package Initialization
"""

from .models import (
    Base,
    User,
    Role,
    Permission,
    UserLoginHistory,
    UserSession,
    user_permissions,
    user_roles,
    role_permissions,
    Permissions,
    Roles,
    create_database_engine,
    create_tables,
    drop_tables,
    get_session
)

from .database_manager import DatabaseManager
from .config import (
    get_database_url,
    create_db_engine,
    init_database,
    get_session_factory,
    get_engine
)

__all__ = [
    # 基础模型
    'Base',
    'User',
    'Role', 
    'Permission',
    'UserLoginHistory',
    'UserSession',
    
    # 关联表
    'user_permissions',
    'user_roles',
    'role_permissions',
    
    # 常量
    'Permissions',
    'Roles',
    
    # 基础工具函数
    'create_database_engine',
    'create_tables',
    'drop_tables',
    'get_session',
    
    # 数据库管理器
    'DatabaseManager',
    
    # 配置相关
    'get_database_url',
    'create_db_engine',
    'init_database',
    'get_session_factory',
    'get_engine'
]
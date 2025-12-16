"""
基于SQLAlchemy的用户、角色、权限表模型
使用PostgreSQL数据库配置
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os

# 获取数据库配置
from settings import DATABASE_CONFIG

# 创建基础类
Base = declarative_base()

# 用户-角色关联表（多对多关系）
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

# 角色-权限关联表（多对多关系）
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

# 用户-权限关联表（多对多关系）
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar = Column(String(255))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    date_joined = Column(DateTime, default=func.now(), nullable=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    permissions = relationship('Permission', secondary=user_permissions, back_populates='users')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Role(Base):
    """角色表"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', code='{self.code}')>"


class Permission(Base):
    """权限表"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    users = relationship('User', secondary=user_permissions, back_populates='permissions')
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
    
    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint('code', 'category', name='uq_permission_code_category'),
    )
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', code='{self.code}', category='{self.category}')>"


def get_postgresql_url():
    """获取PostgreSQL数据库连接URL"""
    # 优先使用环境变量
    db_url = os.getenv('DB_URI')
    if db_url:
        return db_url
    
    # 使用settings中的PostgreSQL配置
    postgresql_config = DATABASE_CONFIG.get('postgresql', {})
    url = postgresql_config.get('url', 'postgresql://icefox:123456@localhost:5432/kghub?sslmode=disable')
    
    # 如果url是os.getenv格式的，需要解析
    if url.startswith('os.getenv'):
        # 提取默认值
        import re
        # 匹配os.getenv("DB_URI", "postgresql://...")格式
        match = re.search(r'os.getenv\s*\(\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)', url)
        if match:
            env_var = match.group(1)
            default_url = match.group(2)
            # 再次检查环境变量
            env_value = os.getenv(env_var)
            url = env_value if env_value else default_url
    
    return url


def create_database_engine():
    """创建数据库引擎"""
    database_url = get_postgresql_url()
    echo = os.getenv('DB_ECHO', 'False').lower() == 'true'
    
    engine = create_engine(
        database_url,
        echo=echo,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    return engine


def create_tables(engine):
    """创建所有表"""
    Base.metadata.create_all(engine)
    print("✓ 所有表创建成功")


def drop_tables(engine):
    """删除所有表"""
    Base.metadata.drop_all(engine)
    print("✓ 所有表删除成功")


def get_session(engine):
    """获取数据库会话"""
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    print("开始初始化数据库...")
    
    # 创建数据库引擎
    engine = create_database_engine()
    print(f"✓ 数据库引擎创建成功: {engine.url}")
    
    # 创建所有表
    create_tables(engine)
    
    # 创建会话
    session = get_session(engine)
    
    try:
        # 检查是否已有数据
        existing_user = session.query(User).first()
        if existing_user:
            print("数据库中已有数据，跳过初始化")
        else:
            print("开始创建基础数据...")
            
            # 创建基础权限
            permissions = [
                Permission(name="查看用户", code="user.view", category="用户管理"),
                Permission(name="创建用户", code="user.create", category="用户管理"),
                Permission(name="编辑用户", code="user.edit", category="用户管理"),
                Permission(name="删除用户", code="user.delete", category="用户管理"),
                Permission(name="查看角色", code="role.view", category="角色管理"),
                Permission(name="创建角色", code="role.create", category="角色管理"),
                Permission(name="编辑角色", code="role.edit", category="角色管理"),
                Permission(name="删除角色", code="role.delete", category="角色管理"),
                Permission(name="查看权限", code="permission.view", category="权限管理"),
                Permission(name="创建权限", code="permission.create", category="权限管理"),
                Permission(name="编辑权限", code="permission.edit", category="权限管理"),
                Permission(name="删除权限", code="permission.delete", category="权限管理"),
            ]
            
            session.add_all(permissions)
            session.flush()
            print(f"✓ 创建了 {len(permissions)} 个基础权限")
            
            # 创建基础角色
            roles = [
                Role(name="超级管理员", code="super_admin", description="拥有所有权限的超级管理员"),
                Role(name="管理员", code="admin", description="系统管理员"),
                Role(name="普通用户", code="user", description="普通用户"),
                Role(name="访客", code="guest", description="访客用户"),
            ]
            
            session.add_all(roles)
            session.flush()
            print(f"✓ 创建了 {len(roles)} 个基础角色")
            
            # 为超级管理员分配所有权限
            super_admin_role = session.query(Role).filter_by(code="super_admin").first()
            if super_admin_role:
                super_admin_role.permissions.extend(permissions)
                print("✓ 为超级管理员分配了所有权限")
            
            # 为管理员分配管理权限
            admin_role = session.query(Role).filter_by(code="admin").first()
            if admin_role:
                admin_permissions = [p for p in permissions if p.category in ["用户管理", "角色管理", "权限管理"]]
                admin_role.permissions.extend(admin_permissions)
                print("✓ 为管理员分配了管理权限")
            
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="系统管理员",
                is_active=True,
                is_superuser=True,
                is_staff=True
            )
            admin_user.password_hash = "pbkdf2:sha256:260000$example$salt$hash"  # 示例密码哈希
            
            session.add(admin_user)
            session.flush()
            print("✓ 创建了默认管理员用户")
            
            # 为管理员用户分配超级管理员角色
            admin_user.roles.append(super_admin_role)
            print("✓ 为管理员用户分配了超级管理员角色")
            
            # 提交所有更改
            session.commit()
            print("✓ 基础数据创建完成")
        
    except Exception as e:
        session.rollback()
        print(f"✗ 初始化过程中出现错误: {e}")
        raise
    finally:
        session.close()
        print("数据库初始化完成")
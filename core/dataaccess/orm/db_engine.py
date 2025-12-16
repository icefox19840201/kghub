import os,re
from sqlalchemy import create_engine
from settings import DATABASE_CONFIG

def get_postgresql_url():
    """获取PostgreSQL数据库连接URL"""
    db_url = os.getenv('DB_URI')
    if db_url:
        return db_url

    # 使用settings中的PostgreSQL配置
    postgresql_config = DATABASE_CONFIG.get('postgresql', {})
    url = postgresql_config.get('url')

    # 如果url是os.getenv格式的，需要解析
    if url.startswith('os.getenv'):
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
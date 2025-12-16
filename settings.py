from starlette.templating import Jinja2Templates
import os
template_dir=os.path.join(os.path.dirname(__file__),"templates")
template=Jinja2Templates(directory=str(template_dir))
# 数据库配置
DATABASE_CONFIG = {
    'postgresql': {
        'url': 'os.getenv("DB_URI", "postgresql://icefox:123456@localhost:5432/kghub?sslmode=disable")',
        'echo': False
    },
    'mysql': {
        'url': 'mysql+pymysql://username:password@localhost:3306/kghub',
        'echo': False
    }
}


llm={

}
embeddings={

}
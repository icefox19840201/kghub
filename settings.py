from starlette.templating import Jinja2Templates
import os
template_dir=os.path.join(os.path.dirname(__file__),"templates")
template=Jinja2Templates(directory=str(template_dir))
db={
    'mysql':'mysql+pymysql://icefox1:123456@localhost:3306/text_to_sql',
    'pg':'postgresql://icefox:123456@localhost:5432/postgres?sslmode=disable'
}
llm={
'qwen':{
    'model':'qwen3-max',
    'temperature':{
        'text-to-sql':0
    }
}
}
embeddings={
'bge':r'E:\bigmodel\huggingface_model\bge-base-zh-v1.5',
'transformers':'D:\bigmodel\sentence-transformers'
}
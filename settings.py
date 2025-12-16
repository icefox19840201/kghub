from starlette.templating import Jinja2Templates
import os
template_dir=os.path.join(os.path.dirname(__file__),"templates")
template=Jinja2Templates(directory=str(template_dir))
db={
    
}
llm={

}
embeddings={

}
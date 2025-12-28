from langchain_openai import ChatOpenAI
import settings
def getllm():
    model=settings.llm.get('qwen').get('model')
    temperature=settings.llm.get('qwen').get('temperature').get('text-to-sql')
    llm=ChatOpenAI(model=model, temperature=temperature)
    return llm
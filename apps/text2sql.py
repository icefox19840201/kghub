from fastapi import Request
from starlette.responses import StreamingResponse
from core.schemas.default import Query
from core.biziness.texttosql import stream_sql_query
import json
class TextToSql:
    async def query(self,request:Request,query:Query):
        q=query.question
        async def generate():
            result=stream_sql_query(q)
            async for chunk in result:
                yield json.dumps({'content': chunk}) + '\n'
        return StreamingResponse(generate(), media_type="text/event-stream")
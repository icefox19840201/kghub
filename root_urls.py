import initapp
from urls.sys_urls import sys_router
from urls.accounts_url import account_router
app=initapp.fastapi_init()
app.include_router(sys_router,prefix='/default',tags=['系统功能'])
app.include_router(account_router,prefix='/accounts',tags=['用户管理'])
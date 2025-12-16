from fastapi import APIRouter
from apps.account.account import Account
account_router=APIRouter()
account=Account()
account_router.add_api_route(path='/login',methods=['post'],endpoint=account.login,description='用户登录')
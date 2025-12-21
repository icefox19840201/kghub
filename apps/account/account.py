from core.base.viewbase import BaseView
from fastapi import Request
from core.schemas.account import LoginRequest
from core.biziness.account import AccountInfo
class Account(BaseView):
    def __init__(self):
        self.account=AccountInfo()
    async def login(self,request:Request,account:LoginRequest):
        """
        登录
        :param request:
        :param account:
        :return:
        """
        user_name=account.username
        password=account.password
        print(user_name,password)
        ret=self.account.auth_user(user_name,password)
        if ret:
            return {'success':1,'message':'登录成功'}
        return {'success':0,'message':'用户名或密码错误'}

    async def logout(self,request:Request):
        """
        登出
        :param request:
        :return:
        """
        pass
    async def create_user(self,request:Request):
        """
        注册
        :param request:
        :return:
        """
        pass

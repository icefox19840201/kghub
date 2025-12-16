from core.base.viewbase import BaseView
from fastapi import Request
from core.schema.account import LoginRequest
class Account(BaseView):
    async def login(self,request:Request,account:LoginRequest):
        """
        登录
        :param request:
        :param account:
        :return:
        """
        pass
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

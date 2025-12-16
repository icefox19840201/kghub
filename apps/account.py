from core.base.viewbase import BaseView
from fastapi import Request
from core.schema.account import Login_account
class Account(BaseView):
    async def login(self,request:Request,account:Login_account):
        """
        登录
        :param request:
        :param account:
        :return:
        """
        pass
from pydantic import BaseModel,Field
from typing import Optional
class Login_account(BaseModel):
    account_name:str=Field(...,description='账户名称')
    account_password:str=Field(...,description='账户密码')
from core.dataaccess.orm.Account import AccountInfo
class AccoutInfo:
    def __init__(self):
        self.account=AccountInfo()

    def  auth(self,user,pwd)-> bool:
        '''
        验证有效用户
        :param user:
        :param pwd:
        :return:
        '''
        return self.account.auth_user(user,pwd)
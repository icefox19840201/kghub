from sqlalchemy.orm import  sessionmaker
from core.dataaccess.orm.db_engine import create_database_engine
from core.dataaccess.orm.models import User
class AccountInfo:
    def __init__(self):
        engine =create_database_engine()
        self.Session = sessionmaker(bind=engine)
    def auth_user(self,user,pwd)->bool:
        '''
        验证是否为有效用户
        :param user:
        :param pwd:
        :return:
        '''
        user = self.Session.query(User).filter((User.username==user)|(User.email==user),User.password_hash==pwd).first()
        if user:
            return True
        return False
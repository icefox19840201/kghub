from settings import template
class BaseView:
    def __init__(self):
        self.template=template
        self.check_right()
    def check_right(self):
        '''
        权限校验
        :return:
        '''
        pass
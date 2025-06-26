class SendMailError(Exception):
    def __init__(self, msg='发送邮件异常'):
        super().__init__(msg)
import smtplib
import traceback
from email.mime.text import MIMEText
from email.utils import formataddr

from common.err.smtp import SendMailError


class SendMail:

    def __init__(
        self,
        from_mail: str,
        to_mail: str,
        auth_code: str,
        smtp_host: str = 'smtp.qq.com',
        smtp_port: int = 465
    ):
        """
        邮箱发送类
        :param from_mail: 发送者邮箱
        :param to_mail: 接收者邮箱
        :param auth_code: 发送者邮箱 smtp 授权码
        :param smtp_host:
        :param smtp_port:
        """
        self.__from_mail = from_mail
        self.__to_mail = to_mail
        self.__auth_code = auth_code
        self.__smtp_host = smtp_host
        self.__smtp_port = smtp_port

    def send(self, subject: str, content: str, mime_type: str = 'plain'):
        """
        发送邮件
        :param subject: 邮件标题
        :param content: 邮件内容
        :param mime_type: 邮件内容对应的 mime 类型(如: plain/html)
        :return:
        """
        try:
            msg = MIMEText(content, mime_type, 'utf-8')
            msg['From'] = formataddr(('From', self.__from_mail), 'utf-8')  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(('To', self.__to_mail), 'utf-8')  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = subject  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL(self.__smtp_host, self.__smtp_port)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(self.__from_mail, self.__auth_code)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.__from_mail, [self.__to_mail, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接

        except Exception as e:
            raise SendMailError(f'发送邮件异常: {traceback.format_exc()}')
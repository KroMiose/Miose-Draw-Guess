from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import datetime


class MioseBotOpt:
    def __init__(self, mak):
        self.host_server = 'smtp.163.com'
        self.sender = 'kromiose@163.com'
        self.send_name = '谬锶bot'

        self.ep_code = mak


    def send_mail(self, recv_mail, title, context):
        """ 发送邮件
        
        Keyword arguments:
        recv_mail -- 接收者邮件地址
        title   -- 邮件标题
        context -- 邮件正文
        Return: 是否成功
        """
        
        from_mail, send_name = self.sender, self.send_name
        mail_title, mail_content = title, context

        smtp = SMTP_SSL(self.host_server)
        smtp.ehlo(self.host_server)
        smtp.login(self.sender, self.ep_code)
        msg = MIMEText(mail_content, "html", 'utf-8')
        msg['Subject'] = Header(mail_title, 'utf-8')
        msg['From'] = MioseBotOpt._format_addr(u'%s <%s>' % (send_name, from_mail))
        msg['To'] = MioseBotOpt._format_addr(u'%s <%s>' % (recv_mail, recv_mail))
        try:    # 发送邮件
            smtp.sendmail(from_mail, recv_mail, msg.as_string())
            smtp.quit()
        except Exception as e:
            print('[ERROR]:', e)
            return False
        return True

    @staticmethod
    def _format_addr(s):
        return formataddr(parseaddr(s))


if __name__ == '__main__':

    mbot = MioseBotOpt('RCHNMWKGWDSZLEXB')  # 实例化时填入163邮箱IMAP/SMTP授权码
    # mbot.send_mail('2569016032@qq.com', '谬锶快报测试', '谬锶快报正文')



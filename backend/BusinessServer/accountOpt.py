from utils.dbManager import DatabaseManager
from utils.mailBot import MioseBotOpt
from utils.md5 import hex_md5
import sys
import random
import time
from copy import deepcopy

sys.path.append("..") 
from config import BusinessServerConfig as config


class accountOpt:
    mBot = MioseBotOpt(config.mail_access_key)
    email_addr_code = []    # 暂存邮件地址与验证码对应

    def __init__(self):
        self.db = DatabaseManager(config=config.database_settings)


    # 用户注册 * 返回是否成功
    def register(self, username, credential, email, rcode):
        if username.find('@') != -1:
            return ('error', '不合法的输入')
        if self.checkText(username) and self.checkText(credential) and self.checkText(email):
            credential = hex_md5(credential + config.md5_salt)
            if self.verify_email(email, rcode):
                if not self.db.select(f'''SELECT * FROM `user` WHERE `username` = '{username}' OR `email` = '{email}' ;'''):
                    sql = f'''INSERT INTO `user` (`username`, `credential`, `email`) VALUES ('{username}', '{credential}', '{email}');'''
                    if(self.db.execute(sql)):
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {username} 注册成功")
                        return ('success', '注册成功')
                else:
                    return ('error', '用户名或邮箱已存在')
            else:
                return ('error', '邮箱验证失败')
        return ('error', '不合法的输入')

    # 用户登录 * 返回用户uid
    def login(self, credential, username=''):
        credential = hex_md5(credential + config.md5_salt)
        if username and self.checkText(username):
            res = self.db.select(f'''SELECT * FROM `user` WHERE `username` = '{username}' AND `credential` = '{credential}';''')
            if(len(res)):
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {res[0]['username']} 使用用户名登录成功")
                return res[0]['uid'], res[0]['username']
        if username and self.checkText(username):
            res = self.db.select(f'''SELECT * FROM `user` WHERE `email` = '{username}' AND `credential` = '{credential}';''')
            if(len(res)):
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {res[0]['username']} 使用邮箱登录成功")
                return res[0]['uid'], res[0]['username']
        return None, None

    # 发送确认邮件 * 返回是否成功
    def send_verify_email(self, email):
        if self.checkText(email):
            if len(self.db.select(f'''SELECT * FROM `user` WHERE `email` = '{email}' ;''')) == 0:
                rcode = random.randint(1000, 10000)
                for i, v in enumerate(self.email_addr_code):
                    if email == v['email']:
                        self.email_addr_code[i]['code'] = rcode
                        self.email_addr_code[i]['send_time'] = time.time()
                        break
                else:
                    self.email_addr_code.append({
                        'email': email,
                        'code': rcode,
                        'send_time': time.time(),
                    })
                if self.mBot.send_mail(email, '邮件验证码', f"您的注册邮件验证码是: {rcode}"):
                    return True
        return False

    # 邮件验证 * 返回是否成功
    def verify_email(self, email, rcode):
        if self.checkText(email):
            for e in deepcopy(self.email_addr_code):
                if email == e['email'] and str(e['code']) == str(rcode):
                    self.email_addr_code.remove(e)
                    return True
        return False

    # 检测输入字符串是否合法
    @staticmethod
    def checkText(text):
        specialKey = "[`^*()=|{}':;'\\[\\]<>/！￥……&*（）——|{}【】‘；：”“'。，、？]‘'"
        for k in specialKey:
            if text.find(k) != -1:
                return False
        return True


if __name__ == '__main__':
    ao = accountOpt()

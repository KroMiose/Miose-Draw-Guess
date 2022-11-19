from utils.dbManager import DatabaseManager
from utils.mailBot import MioseBotOpt
from utils.md5 import hex_md5
import sys
import random
import time
from copy import deepcopy

sys.path.append("..") 
from config import BusinessServerConfig as config


class dataOpt:
    def __init__(self):
        self.db = DatabaseManager(config=config.database_settings)

    # 获取随机词汇
    def get_random_word(self, num):
        res = self.db.select(f'''SELECT * FROM `words` ORDER BY RAND() LIMIT {num};''')
        return res

    # 检测输入字符串是否合法
    @staticmethod
    def checkText(text):
        specialKey = "[`^*()=|{}':;'\\[\\]<>/！￥……&*（）——|{}【】‘；：”“'。，、？]‘'"
        for k in specialKey:
            if text.find(k) != -1:
                return False
        return True


if __name__ == '__main__':
    do = dataOpt()

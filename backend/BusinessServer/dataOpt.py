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

    # 获取词汇来源列表
    def get_word_source_list(self):
        try:
            res = self.db.select(f'''SELECT DISTINCT `source` FROM `words`;''')
            return [s['source'] for s in res]
        except Exception as e:
            return []

    # 获取随机词汇
    def get_random_word(self, num, reqData):
        try:
            sourceList = reqData.get('source')
            # 从数据库中抽取分类中的词汇
            if sourceList:
                sourceList = [f"'{i}'" for i in sourceList]
                sourceList = ','.join(sourceList)
                res = self.db.select(f"SELECT * FROM `words` WHERE `source` IN ({sourceList}) ORDER BY RAND() LIMIT {num}")
            else:
                res = self.db.select(f'''SELECT * FROM `words` ORDER BY RAND() LIMIT {num};''')
            return res
        except Exception as e:
            return []

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

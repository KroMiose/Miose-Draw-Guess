import pymysql
import re

class DatabaseManager:
    debug = False

    def __init__(self, config):
        self.conn = pymysql.connect(
            host=config['mysql_host'],
            port=int(config['mysql_port']),
            user=config['mysql_user'],
            passwd=config['mysql_passwd'],
            db=config['mysql_db'],
            autocommit=True
        )
        self.debug = config['enable_debug']
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
    
    def select(self, sql):
        """查询"""
        self.conn.ping(reconnect=True)
        if(self.debug):
            print('正在执行SQL语句: ' + sql)
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    def execute(self, sql):
        """更新/新增/删除"""
        try:
            self.conn.ping(reconnect=True)
            if(self.debug):
                print('正在执行SQL语句: ' + sql)
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False

    def sqlAttackCheck(self, text):
        """" 文本SQL注入检测，返回是否合法 """
        
        v = str(text).lower()
        pattern = r"\b(and|like|exec|insert|select|drop|grant|alter|delete|update|count|chr|mid|master|truncate|char|delclare|or)\b|(\*|;)"
        r = re.search(pattern,v)
        return False if r else True
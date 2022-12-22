# 妙思猜绘 后端服务应用程序模板配置文件
# 请将此文件复制一份并重命名为 config.py 后再进行修改

class BusinessServerConfig:
    """ 业务服务应用程序配置选项 """
    
    # 业务服务器 host:port
    server_host = 'dg.kromiose.top'
    server_port = 2900

    # 是否处于debug模式
    debug = True

    # 房间信息拉取更新间隔时间
    room_update_itv = 3

    # 游戏服务器列表
    GameServerHostList = [
        '127.0.0.1:2910',
    ]

    # 数据库连接配置
    database_settings = {
        'mysql_host': 'localhost',
        'mysql_port': '3306',
        'mysql_user': 'root',
        'mysql_passwd': '',
        'mysql_db': 'miose_draw_guess',
        'enable_debug': False,
    }

    # 网易云邮箱IMAP/SMTP授权码(**不是邮箱密码**)
    mail_access_key = ''
    # md5加盐值
    md5_salt = '@MioseSalt'
    # 服务授权码(**必须与下方游戏服务器配置项一致**)
    server_access_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

    # 游戏进程配置参数
    game_configs = {
        'max_round': 3,             # 最大轮数
        'selection_duration': 15,   # 选择题目时间 - 秒
        'transition_duration': 1,   # 游戏过渡时间 - 秒
        'draw_duration': 90,        # 画图时间 - 秒
        'comment_duration': 12,     # 评论时间 - 秒
        'word_pool_size': 5,    # 待选词汇池大小
    }

class GameServerConfig:
    """ 游戏服务应用程序配置选项 """
    
    # 游戏服务器 host:port
    server_host = 'localhost'
    server_port = 2910

    # 服务授权码(**必须与上方业务服务器配置项一致**)
    server_access_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

    # 游戏进程配置参数
    game_configs = BusinessServerConfig.game_configs

    # 房间不活跃自动销毁时间 (秒)
    room_expire_time = 300

from time import sleep
from flask import Flask, redirect, request, session
from flask_cors import CORS
import os
import sys
import json
import time
import random
import requests
import uuid

from geventwebsocket.handler import WebSocketHandler  # 提供WS（websocket）协议处理
from geventwebsocket.server import WSGIServer   # websocket服务承载
from geventwebsocket.websocket import WebSocket # websocket语法提示

sys.path.append("..") 
from config import BusinessServerConfig as config

app = Flask(__name__)
CORS(app, supports_credentials=True)

from accountOpt import accountOpt
ao = accountOpt()

# 测试服务器连通性接口
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    time.sleep(3)
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ping from {request.remote_addr} with data: {reqData}")
    return {'code': 'success', 'msg': 'welcome to Miose_Draw_Guess', 'data': reqData}

# 用户注册接口 & 接收参数: username, credential, email, mail_code
@app.route('/register', methods=['POST'])
def register():
    reqData = json.loads(request.data.decode('UTF-8'))
    # print(request.data)
    if 'username' in reqData and 'credential' in reqData and 'email' in reqData and 'verify_code' in reqData:
        code, msg = ao.register(reqData['username'], reqData['credential'], reqData['email'], reqData['verify_code'])
        return {'code': code, 'msg': msg}
    return {'code': 'error', 'msg': '参数缺失'}

# 用户请求验证邮件接口 & 接收参数: email
@app.route('/req_email_vertify', methods=['POST'])
def req_email_vertify():
    reqData = json.loads(request.data.decode('UTF-8'))
    # print(reqData)
    if 'email' in reqData and reqData['email']:
        if ao.send_verify_email(reqData['email']):
            return {'code': 'success', 'msg': '邮件验证码已发送'}
    return {'code': 'error', 'msg': '邮件发送失败，请检查邮箱输入'}

# 用户登录接口 & 接收参数: username, credential
@app.route('/login', methods=['POST'])
def login():
    reqData = json.loads(request.data.decode('UTF-8'))
    # print(request.data)
    userid, username = None, None
    if 'credential' in reqData and 'username' in reqData:
        userid, username = ao.login(credential=reqData['credential'], username=reqData['username'])
        if userid is not None:
            session['userid'] = userid
            session['username'] = username
            session.permanent = True
            return {'code': 'success', 'msg': '登录成功', 'username': username}
    return {'code': 'error', 'msg': '登录失败，请检查输入'}

# 用户登出 & 需登录
@app.route('/logout', methods=['GET'])
def logout():
    session['userid'] = False
    session['username'] = False
    return {'code': 'success'}


""" ================================ 房间管理接口 ================================ """

last_updateTime = 0
curRooms = []

# 获取房间列表 & 需登录
@app.route('/list_rooms', methods=['POST'])
def list_rooms():
    global last_updateTime, curRooms
    if session.get('userid'):
        if time.time() - last_updateTime >= config.room_update_itv:
            curRooms = []
            for gs in config.GameServerHostList:
                res = json.loads(requests.post(f"http://{gs}/get_room_list").text)
                if res['code'] == 'success':
                    curRooms = curRooms + res.get('data')
            last_updateTime = time.time()
        return {'code': 'success', 'rooms': curRooms}
    return {'code': 'error'}

# 创建房间 & 需登录
@app.route('/create_room', methods=['POST'])
def creat_room():
    reqData = json.loads(request.data.decode('UTF-8'))
    uid = session.get('userid')
    if uid and ('hostRoomInfo' in reqData):
        hostKey = str(uuid.uuid4())  # 生成主持密钥，拥有该密钥的玩家为房间主持人，有权进行游戏进程控制
        # gs = config.GameServerHostList[random.randint(0, len(config.GameServerHostList))]
        gs = config.GameServerHostList[0]

        roomId =  random.randint(100000, 1000000)

        res = json.loads(requests.post(f"http://{gs}/new_room", data={
            'sak': config.server_access_key,            # 服务授权码
            'hostKey': hostKey,                         # 主持密钥
            'roomId': roomId,                           # 房间id
            'hostname': session['username'],            # 主持人用户名
            'name': reqData['hostRoomInfo']['name'],                    # 房间名
            'description': reqData['hostRoomInfo']['description'],      # 房间描述
            'max_players_num': reqData['hostRoomInfo']['max_players_num'],      # 房间最大人数
            'password': reqData['hostRoomInfo']['password'],                    # 访问密码
            'locked':( True if reqData['hostRoomInfo']['password'] else False),   # 锁定状态
            'wsUrl': f"ws://{gs}/draw_room",    # 房间ws链接
        }).text)
        if res['code'] == 'success':
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 房间 {reqData['hostRoomInfo']['name']} 创建成功")
            return {
                'code': 'success', 'hostKey': hostKey, 'game_configs': config.game_configs,
                'roomInfo': {
                    'roomId': roomId,                           # 房间id
                    'hostname': session['username'],            # 主持人用户名
                    'name': reqData['hostRoomInfo']['name'],                    # 房间名
                    'description': reqData['hostRoomInfo']['description'],      # 房间描述
                    'max_players_num': reqData['hostRoomInfo']['max_players_num'],      # 房间最大人数
                    'password': reqData['hostRoomInfo']['password'],                    # 访问密码
                    'locked':( True if reqData['hostRoomInfo']['password'] else False),   # 锁定状态
                    'wsUrl': f"ws://{gs}/draw_room",    # 房间ws链接
                }
            }
    return {'code': 'error'}

# 请求加入游戏房间
@app.route('/join_room', methods=['POST'])
def join_room():
    global curRooms
    reqData = json.loads(request.data.decode('UTF-8'))
    if session.get('userid') and session.get('username'):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 接收到来自 {session.get('username')} 的加入房间请求")
        for idx, room in enumerate(curRooms):
            if int(room['id']) == int(reqData.get('roomId')):
                if(int(room['cur_players_num']) < int(room['max_players_num'])):
                    room['cur_players_num'] += 1
                    return {'code': 'success', 'roomInfo': {
                        'roomId': room['id'],           # 房间id
                        'hostname': room['hostname'],   # 主持人用户名
                        'name': room['name'],                # 房间名
                        'description': room['description'],  # 房间描述
                        'max_players_num': room['max_players_num'], # 房间最大人数
                        'wsUrl': room['wsUrl'],         # 房间ws链接
                    }}
    return {'code': 'error'}


# 获取WebSocket url接口
@app.route('/get_public_chat_room_ws')
def get_public_chat_room_ws():
    return {'code': 'success', 'wsUrl': f"ws://{config.server_host}:{config.server_port}/public_chat_room"}
client_list = []

# 公共聊天室ws接口
@app.route('/public_chat_room')
def public_chat_room():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 客户端 {client_socket} 尝试连接")
    client_socket = request.environ.get('wsgi.websocket')
    client_list.append(client_socket)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 客户端 {client_socket} 已连接")
    try:
        while True:
            try:
                msg_from_cli = client_socket.receive()
            except Exception as e:
                return {'code': 'error'}
            #收到任何一个客户端的信息都进行全部转发（注意如果某个客户端连接断开，在遍历发送时连接不存在会报错，需要异常处理）
            for client in client_list:
                try:
                    client.send(msg_from_cli)
                except Exception as e:
                    continue
    except Exception as e:
        client_list.remove(client_socket)
        return {'code': 'error'}

if __name__ == '__main__':
    os.system('cls')
    app.config['SECRET_KEY'] = os.urandom(32)
    # app.run(debug=config.debug, threaded=True, host='0.0.0.0', port=config.server_port)
    http_server = WSGIServer(('0.0.0.0', config.server_port), application=app, handler_class=WebSocketHandler)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 主服务器在 {config.server_host}:{config.server_port} 上运行中...")
    http_server.serve_forever()

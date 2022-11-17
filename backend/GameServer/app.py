from time import sleep
from flask import Flask, redirect, request, session
from flask_cors import CORS
import os
import sys
import json
import time

from geventwebsocket.handler import WebSocketHandler  # 提供WS（websocket）协议处理
from geventwebsocket.server import WSGIServer   # websocket服务承载
from geventwebsocket.websocket import WebSocket # websocket语法提示

sys.path.append("..") 
from config import GameServerConfig as config

app = Flask(__name__)
CORS(app, supports_credentials=True)



# 测试服务器连通性接口
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    # time.sleep(3)
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
        print('check1:',reqData)
    except json.decoder.JSONDecodeError:
        reqData = request.form
        print('check2:',reqData)
    print(f"ping from {request.remote_addr} with data: {reqData}")
    return {'code': 'success', 'msg': 'welcome to Miose_Draw_Guess', 'data': reqData}


""" ================================ 房间管理接口 ================================ """
rooms = []  # 全局房间列表

@app.route('/get_room_list', methods=['POST'])
def get_room_list():
    global rooms
    rooms = [room for room in rooms if len(room['clients']) > 0]
    return {'code': 'success', 'data': [{
        'id': r.get('roomId'),
        'name': r.get('name'),
        'locked': r.get('locked'),
        'description': r.get('description'),
        'hostname': r.get('hostname'),
        'cur_players_num': len(r.get('clients')),
        'max_players_num': r.get('max_players_num'),
        'wsUrl': r.get('wsUrl'),
        'status':  r.get('status'),
    } for r in rooms]}

# 创建房间
@app.route('/new_room', methods=['POST'])
def new_room():
    try:
        reqData = json.loads(request.data.decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        reqData = request.form
    # print(reqData)
    if 'hostKey' in reqData and reqData['sak'] == config.server_access_key:
        print('房间请求授权通过')
        # 通过授权验证
        rooms.append({
            'hostKey': reqData['hostKey'],
            'roomId': reqData['roomId'],
            'hostname': reqData['hostname'],
            'name': reqData['name'],
            'description': reqData['description'],
            'max_players_num': reqData['max_players_num'],
            'password': reqData['password'],
            'locked': reqData['locked'],
            'clients': [],  # 已连接的客户端
            'wsUrl': reqData['wsUrl'],
            'status': 'waiting',
            'ingameData': {
                'userlist': [],
                'status': 'waiting',
                'keyword': '',
            },
        })  # 新建房间
        return {'code': 'success', 'message': 'pass'}
    return {'code': 'error'}


client_list = []
@app.route('/draw_room')
def draw_room():
    client_socket = request.environ.get('wsgi.websocket')
    is_inRoom = False
    curRoom = None

    try:
        while True:
            msg_from_cli = client_socket.receive()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 接收到客户端信息: {msg_from_cli[:20]} (总长度:{len(msg_from_cli)})")

            # 在建立连接后，客户端需要表示自己的身份后予以接入房间，未接入之前不予提供服务
            if not is_inRoom:   # 未加入房间前执行
                try:
                    mdata = json.loads(msg_from_cli)
                    # print('解析结果', mdata)

                    if roomId := mdata.get('roomId'):
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {mdata['sender']} 请求加入房间: {roomId}")
                        for idx, room in enumerate(rooms):
                            if str(room['roomId']) == str(room['roomId']):
                                curRoom = rooms[idx] # 获取到指定房间
                                curRoom['clients'].append({
                                    'socket': client_socket,
                                    'username': mdata['sender'],
                                    'score': 0,
                                    'is_host': True if mdata['sender'] == curRoom['hostname'] else False,
                                })
                                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {mdata['sender']} 已加入房间: {roomId}")
                                is_inRoom = True
                                break
                except Exception as e:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {mdata['sender']} 加入房间出错: {e}")
                    continue
            else:   # 接入房间后执行
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 房间人数: {len(curRoom['clients'])}")

                """ ================================= 主要游戏服务逻辑 ================================= """
                # 广播 JSON字符串 消息
                def sendBoardcast(msg):
                    msg_from_cli = json.dumps(msg)
                    for client in curRoom['clients']:  # 接入房间后，只向指定房间广播消息
                        try:
                            client['socket'].send(msg_from_cli)
                        except Exception as e:
                            curRoom['clients'].remove(client)
                            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 有客户端离线，剩余人数: {len(curRoom['clients'])}")
                            continue
                # 向指定玩家发送 JSON字符串 消息 返回值：是否发送成功
                def sendMsgTo(username, msg):
                    for c in curRoom['clients']:
                        if c['username'] == username:
                            try:
                                c['socket'].send(msg)
                                return True
                            except Exception as e:
                                curRoom['clients'].remove(c)
                                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 有客户端离线，剩余人数: {len(curRoom['clients'])}")
                                continue
                    return False

                try:
                    mdata = json.loads(msg_from_cli)    # 解析ws通讯消息
                    mdata['ingameData'] = curRoom['ingameData']
                    
                    if 'opt' in mdata:  # 有操作指令
                        # 开始游戏指令
                        if mdata['opt'] == 'startGame':
                            curRoom['status'] = 'ingame'
                            sendBoardcast({
                                'type': 'opt',
                                'runMethod': 'run_startGame',
                            })

                        # 开始回合指令
                        elif mdata['opt'] == 'startRound':
                            ...

                        # 确定选词指令
                        elif mdata['opt'] == 'selectWord':
                            ...

                        # 结束阶段指令
                        elif mdata['opt'] == 'endRound':
                            ...

                    else:   # 默认广播原始信息
                        sendBoardcast(mdata)
                except Exception as e:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERRROR: 无法解析的信息格式！")
                    continue

    except Exception as e:  # 失去连接或发生错误后从房间中移除
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 客户端失去连接，剩余人数: {len(curRoom['clients'])}")
        curRoom['clients'].remove(client_socket)
        return {'code': 'error'}

if __name__ == '__main__':
    os.system('cls')
    app.config['SECRET_KEY'] = os.urandom(16)
    # app.run(debug=config.debug, threaded=True, host='0.0.0.0', port=config.server_port)

    http_server = WSGIServer(('0.0.0.0', config.server_port), application=app, handler_class=WebSocketHandler)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 游戏服务器在 {config.server_host}:{config.server_port} 上运行中...")
    http_server.serve_forever()

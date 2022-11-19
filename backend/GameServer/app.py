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
                'hostname': reqData['hostname'],
                'userlist': [],
                'status': 'waiting',
                'curWord': '',
                'curDrawer': '',
                'curDrawerIdx': 0,
                'round': 0,
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
    ingameData = {}

    try:
        while True:
            msg_from_cli = client_socket.receive()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 接收到客户端信息: {msg_from_cli[:20]} (总长度:{len(msg_from_cli)})")

            # 在建立连接后，客户端需要表示自己的身份后予以接入房间，未接入之前不予提供服务
            if not is_inRoom:   # 未加入房间前执行
                try:
                    mdata = json.loads(msg_from_cli)
                    if roomId := mdata.get('roomId'):
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {mdata['sender']} 请求加入房间: {roomId}")
                        for idx, room in enumerate(rooms):
                            if str(room['roomId']) == str(room['roomId']):
                                curRoom = rooms[idx] # 获取到指定房间
                                # 检测用户是否在房间中
                                if mdata['sender'] not in [c['username'] for c in curRoom['clients']]:
                                    curRoom['clients'].append({
                                        'socket': client_socket,
                                        'username': mdata['sender'],
                                        'score': 0,
                                        'got_answer': False,
                                        'is_online': True,
                                        'is_host': True if mdata['sender'] == curRoom['hostname'] else False,
                                    })
                                else:
                                    is_inRoom = True
                                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 用户 {mdata['sender']} 已在房间中")
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
                def sendBoardcast(msg, block=None):
                    msg['ingameData'] = ingameData
                    ingameData['userlist'] = [{'username': c['username'], 'score': c['score']} for c in curRoom['clients']]
                    msg_from_cli = json.dumps(msg)
                    curRoom['clients'] = [c for c in curRoom['clients'] if c['is_online']]
                    for c in curRoom['clients']:  # 接入房间后，只向指定房间广播消息
                        if c['username'] != block:
                            try:
                                c['socket'].send(msg_from_cli)
                            except Exception as e:
                                c['is_online'] = False
                                # curRoom['clients'].remove(c)
                                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 有客户端离线，剩余人数: {len(curRoom['clients'])}")
                                continue
                # 向指定玩家发送 JSON字符串 消息 返回值：是否发送成功
                def sendMsgTo(username, msg):
                    msg['ingameData'] = ingameData
                    msg_from_cli = json.dumps(msg)
                    for c in curRoom['clients']:
                        if c['username'] == username:
                            try:
                                c['socket'].send(msg_from_cli)
                                return True
                            except Exception as e:
                                c['is_online'] = False
                                # curRoom['clients'].remove(c)
                                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 有客户端离线，剩余人数: {len(curRoom['clients'])}")
                                continue
                    return False

                try:
                    # print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 接收到: {msg_from_cli}")
                    mdata = json.loads(msg_from_cli)    # 解析ws通讯消息
                    mdata['ingameData'] = curRoom['ingameData']
                    mdata['ingameData']['userlist'] = [{'username': c['username'], 'score': c['score']} for c in curRoom['clients']]
                    ingameData = curRoom['ingameData']
                    
                    if 'type' in mdata and 'commend' in mdata and mdata['type'] == 'opt':  # 有操作指令
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 房间收到操作指令: '{mdata['commend']}' => 携带数据: {mdata}")
                        
                        if mdata['commend'] == 'startGame':     # 开始游戏指令
                            curRoom['status'] = 'ingame'
                            curRoom['ingameData']['curDrawerIdx'] = -1
                            sendBoardcast({
                                'type': 'opt',
                                'runMethod': 'run_startGame',
                                'showText': '开始游戏',
                            })

                        elif mdata['commend'] == 'startRound':   # 开始回合指令
                            # 推选下一位玩家
                            curRoom['ingameData']['curDrawerIdx'] = curRoom['ingameData']['curDrawerIdx'] + 1 if curRoom['ingameData']['curDrawerIdx'] < len(curRoom['clients']) - 1 else 0
                            curRoom['ingameData']['curDrawer'] = curRoom['clients'][curRoom['ingameData']['curDrawerIdx']]['username']

                            # 发送选词指令
                            sendMsgTo(curRoom['ingameData']['curDrawer'], {
                                'type': 'opt',
                                'runMethod': 'run_selectWord',
                                'showText': '请选词',
                            })

                            sendBoardcast({
                                'type': 'opt',
                                'showText': f"等待玩家 {curRoom['ingameData']['curDrawer']} 选词",
                            }, curRoom['ingameData']['curDrawer'])

                        elif mdata['commend'] == 'selectWord':  # 确定选词指令
                            curRoom['ingameData']['curWord'] = mdata['word']

                            # 发送画图提示
                            sendMsgTo(curRoom['ingameData']['curDrawer'], {
                                'type': 'opt',
                                'runMethod': 'run_startRound',
                                'showText': '题目: ' + curRoom['ingameData']['curWord']['word'],
                            })

                            sendBoardcast({
                                'type': 'opt',
                                'runMethod': 'run_startRound',
                                'showText': f"{curRoom['ingameData']['curDrawer']}正在作画, 提示: {len(curRoom['ingameData']['curWord']['word'])} 个字",
                            }, curRoom['ingameData']['curDrawer'])

                        elif mdata['commend'] == 'endRound':    # 结束阶段指令
                            # 清除玩家回答记录
                            for c in curRoom['clients']:
                                c['got_answer'] = False

                            sendBoardcast({
                                'type': 'opt',
                                'runMethod': 'run_endRound',
                                'showText': '回合结束, 答案揭晓: ' + curRoom['ingameData']['curWord']['word'],
                            })
                            curRoom['ingameData']['curWord'] = ''

                    else:   # 默认广播原始信息
                        if 'msg' in mdata and curRoom['ingameData']['curWord']:
                            # 检测答案
                            if mdata['msg'] == curRoom['ingameData']['curWord']['word']:
                                # 增加玩家分数
                                for c in curRoom['clients']:
                                    if c['username'] == mdata['sender'] and c['username'] != curRoom['ingameData']['curDrawer'] and c['got_answer'] == False:
                                        c['score'] += 1
                                        c['got_answer'] = True
                                        break
                            # 替换答案
                            for a in curRoom['ingameData']['curWord']['word']:
                                mdata['msg'] = mdata['msg'].replace(a, '*')
                            
                            # 检测是否所有玩家都已经回答
                            all_got_answer = True
                            for c in curRoom['clients']:
                                if c['username'] != curRoom['ingameData']['curDrawer'] and c['got_answer'] == False:
                                    all_got_answer = False
                                    break
                            if all_got_answer:
                                # 清除玩家回答记录
                                for c in curRoom['clients']:
                                    c['got_answer'] = False
                                sendBoardcast({
                                    'type': 'opt',
                                    'runMethod': 'run_endRound',
                                    'showText': '回合结束, 答案揭晓: ' + curRoom['ingameData']['curWord']['word'],
                                })
                                curRoom['ingameData']['curWord']['word'] = ''

                        sendBoardcast(mdata)
                except Exception as e:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 房间 {curRoom['roomId']} 广播消息出错: {e}")
                    continue

    except Exception as e:  # 失去连接或发生错误后从房间中移除
        client_socket['is_online'] = False
        curRoom['clients'].remove(client_socket)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {curRoom['roomId']} 客户端失去连接，剩余人数: {len(curRoom['clients'])}")
        return {'code': 'error'}

if __name__ == '__main__':
    os.system('cls')
    app.config['SECRET_KEY'] = os.urandom(16)
    # app.run(debug=config.debug, threaded=True, host='0.0.0.0', port=config.server_port)

    http_server = WSGIServer(('0.0.0.0', config.server_port), application=app, handler_class=WebSocketHandler)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 游戏服务器在 {config.server_host}:{config.server_port} 上运行中...")
    http_server.serve_forever()

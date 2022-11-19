<template>
  <div class="chatContainer">
    <div class="chatRoom" id="chatRoom">
      <ul class="chatList">
        <li v-for="item in recv_data" :key="item.timestamp" :class="['chatInfo', getUsername==item.sender?'chatInfo-you':'']">
          <div class="sender" v-text="item.sender"></div>
          <div class="msg-box" v-text="item.msg"></div>
        </li>
      </ul>
    </div>
    <div class="chatInputer">
      <el-input v-model="inputText" @keyup.enter.native="send()" maxlength="100" show-word-limit></el-input>
      <el-button type="primary" @click="send()" :disabled="sended">发送</el-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    syncFlag: Boolean,
  },
  data() {
    return {
      ws: null,
      inputText: '',
      recv_data: [
        {
          sender: '谬锶Bot',
          msg: '谬锶Bot在线提示您，请注意文明发言'
        }
      ],
      sended: false,
      wsUrl: '',
    }
  },
  computed: {
    getUsername() {
      return this.$store.state.username
    },
  },
  mounted() {
    let _this = this
    console.log('chatBoard mounted')
    if(this.ws) { // 关闭原有ws连接
      this.ws.close()
    }
    if(this.$route.name === 'index') {
      this.$http({
        method: 'GET',
        url: '/api/get_public_chat_room_ws'
      })
        .then((res) => {
          if(res.data.code === 'success') {
            _this.wsUrl = res.data.wsUrl
            _this.connectToChatRoom(_this.wsUrl)
          } else {
            _this.$message({type: 'error', message: '获取WebSocket链接失败', duration: 2000})
          }
        })
        .catch((err) => {
          console.log(err)
          _this.$message({type: 'error', message: '获取WebSocket链接失败', duration: 2000})
        })

    } else if (this.$route.name === 'room') {
      const roomInfo = this.$store.state.curRoom
      this.connectToChatRoom(roomInfo.wsUrl)
    }
  },
  beforeUnmount() {
    if(this.ws) {
      console.log('关闭原有ws连接')
      this.ws.close()
    }
  },
  methods: {
    submitPath(data) {
      // if(this.$store.state.curPath) {
      //   console.log('sending', this.$store.state.curPath)
      //   this.ws.send(this.$store.state.curPath)
      // }
      if(data) {
        if(this.ws && this.ws.readyState == 1){
          console.log(this.ws)
          this.ws.send(data)
        }
      }
    },
    connectToChatRoom(wsUrl) {
      let _this = this
      this.ws = new WebSocket(wsUrl);
      console.log('正在连接', wsUrl)

      this.ws.onopen = function (MessageEvent) {
        console.log('ws连接成功')
        if (_this.$route.name === 'room') {
          let timestamp = (new Date()).valueOf();
          let sendData = {
            sender: _this.getUsername, // 发送者
            roomId: _this.$store.state.curRoom.roomId, // 房间id
            timestamp: timestamp, // 发送时间
            type: "join", // 消息类型
          }
          _this.ws.send(JSON.stringify(sendData))
        }
      }

      this.ws.onmessage = function (MessageEvent) {
        // console.log(MessageEvent)
        // console.log(MessageEvent.data)
        let data = JSON.parse(MessageEvent.data)
        if(data.type === "chat") {
          console.log(data)
          _this.recv_data.push(JSON.parse(MessageEvent.data))
          setTimeout(() => {
            _this.scrollDown()
          }, 50);
        } else {
          _this.$emit('wsOnRecv', data)
          // if(data.type === 'path') {
            // console.log('recived')
          // }
        }
      }

      this.ws.onclose = function (e) {
        // console.log('websocket 断开');
        // console.log(e)
        console.log(e.code + ' ' + e.reason + ' ' + e.wasClean);
        _this.$message({type: 'error', message: 'WebSocket断开', duration: 1000})
        // setTimeout(() => {_this.connectToChatRoom(wsUrl)}, 5000)
      }

      this.ws.onerror = function (MessageEvent) {
        _this.$message({type: 'error', message: 'WebSocket连接出错，5秒后自动重连', duration: 1000})
        setTimeout(() => {_this.connectToChatRoom(wsUrl)}, 5000)
      }
    },
    send() {
      try{
        let msg = this.inputText
        if(!this.sended) {
          if(msg) {
            let timestamp = (new Date()).valueOf();
            // console.log('sending:', msg)
            this.ws.send(JSON.stringify({sender:this.getUsername, msg, timestamp, type:'chat'}));
            this.inputText = ''
            this.sended = true
            setTimeout(() => {this.sended = false;}, 1000)
          } else {
            this.$message({type: 'error', message: '不能发送空内容哦!', duration: 1500})
          }
        } else {
          this.$message({type: 'error', message: '发送信息过于频繁', duration: 1500})
        }
      } catch (e) {
        this.$message({type: 'error', message: e, duration: 1500})
      }
    },
    scrollDown() {
      let chatRoom = document.getElementById('chatRoom');
      chatRoom.scrollTop = chatRoom.scrollHeight - chatRoom.clientHeight;
      
    },
  }
}
</script>

<style lang="scss" scoped>
.chatContainer {
  flex: 0.8;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;

  .chatRoom::-webkit-scrollbar { width: 0 !important }
  .chatRoom { -ms-overflow-style: none; }
  .chatRoom { overflow: -moz-scrollbars-none; }

  .chatRoom {
    width: 100%;
    background-color: #fff3;
    box-shadow: #0003 4px 4px 16px;
    border-radius: 18px;
    height: 0;
    flex: 1 0 auto;
    overflow-y: scroll;

    .chatList {
      padding: 20px;

      .chatInfo {
        margin-bottom: 5px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;

        .sender {
          color: #feb;
          text-shadow: 2px 2px 12px #000c;
          margin-bottom: 5px;
        }

        .msg-box {
          margin: 0 20px;
          padding: 12px;
          border-radius: 0 20px 20px 20px;
          width: auto;
          background-color: #feb6;
          border: #feb7 solid 1px;
          box-shadow: #0003 4px 4px 16px;
        }
      }

      .chatInfo-you {
        align-items: flex-end;
        .sender {
          color: #9fa;
        }
        .msg-box {
          border-radius: 20px 0 20px 20px;
          background-color: #afa6;
          border: #afa3 solid 1px;
        }
      }
    }
  }

  .chatInputer {
    margin-top: 10px;
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;

    .el-input__inner {
      border-radius: 16px;
      overflow: hidden;
    }
  }
}
</style>
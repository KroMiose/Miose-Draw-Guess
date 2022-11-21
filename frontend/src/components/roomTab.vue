<template>
  <div class="roomTab">
    <div class="roomTabHeader">
      <div class="left">
        <p>房间列表</p>
        <span>(共找到{{roomList.length}}个房间)</span>
      </div>
      <div>
        <el-button type="success" size="mini"  @click="dialogVisible = true"><i class="el-icon-plus"></i>主持</el-button>
        <el-button type="primary" size="mini" @click="reloadRooms()"><i class="el-icon-refresh"></i></el-button>
      </div>
    </div>
    <div class="roomListWindow">
      <ul class="roolList" :loading="loading">
        <li v-for="item in roomList" :key="item.id" :class="['room', item.status]">
          <div class="side">
            <p class="room-name">
              {{item.name}}<i v-show="item.locked != 'False'" class="el-icon-lock"></i>
            </p>
            <p class="room-desc">
              {{item.word_sources}}
            </p>
          </div>
          <div class="side">
            <p class="room-hostname">
              主持人:{{item.hostname}}
              <span :class="['player-num', item.cur_players_num==item.max_players_num?'player-num-full':'']">{{item.cur_players_num + '/' + item.max_players_num}}</span>
            </p>
            <p class="room-hostname">
              <el-button v-show="item.status == 'waiting'" type="success" size="mini" @click="joinRoom(item.id)">进入房间</el-button>
              <el-button v-show="item.status != 'waiting'" type="warning" size="mini" disabled>游戏中</el-button>
            </p>
          </div>
        </li>
      </ul>
    </div>

    <el-dialog
      title="主持游戏"
      :visible.sync="dialogVisible"
      width="400px">
      <div class="row">
        <span>房间名:</span>
        <el-input v-model="hostRoomInfo.name" placeholder="给房间起个好听的名字吧~"></el-input>
      </div>
      <div class="row">
        <span>房间描述:</span>
        <el-select v-model="hostRoomInfo.word_sources" multiple placeholder="请选择词库源">
          <el-option
            v-for="item in word_sources" :key="item" :label="item" :value="item"
          >
          </el-option>
        </el-select>
        <!-- <el-input v-model="hostRoomInfo.description" placeholder="简单描述一下吧~"></el-input> -->
      </div>
      <div class="row">
        <span>访问密码:</span>
        <el-input type="password" v-model="hostRoomInfo.password" placeholder="留空即为公开房间"></el-input>
      </div>
      <div class="row">
        <span>最大玩家数:</span>
        <div class="number-input">
          <i class="el-icon-remove-outline icn" @click="changePlayerNum(-1)"></i>
          <el-input type="number" v-model="hostRoomInfo.max_players_num"></el-input>
          <i class="el-icon-circle-plus-outline icn" @click="changePlayerNum(1)"></i>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="warning" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHostRoomInfo()">创建房间</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  mounted() {
    this.hostRoomInfo.name = this.getUsername + ' 的房间'
    setTimeout(() => {this.loading = false}, 500)
    this.reloadRooms()
    // 获取词库来源列表
    this.$http.get('/api/get_word_source_list').then(res => {
      this.word_sources = res.data.data
    })
  },
  data() {
    return {
      loading: true,
      dialogVisible: false,
      playerNumLimit: [2, 10],
      hostRoomInfo: {
        name: '',
        // description: '',
        max_players_num: 8,
        password: '',
        word_sources: ['基本'],
      },
      roomList: [],
      word_sources: [],
    }
  },
  computed: {
    getUsername() {
      return this.$store.state.username
    },
  },
  methods: {
    changePlayerNum(val) {
      this.hostRoomInfo.max_players_num = (
        this.hostRoomInfo.max_players_num + val >= this.playerNumLimit[0]
        ) && (this.hostRoomInfo.max_players_num + val <= this.playerNumLimit[1]) ?
        this.hostRoomInfo.max_players_num + val : this.hostRoomInfo.max_players_num
    },
    // 申请主持房间
    submitHostRoomInfo() {
      let _this = this
      _this.$message({type: 'info', message: '创建房间中', duration: 1000})

      if(this.hostRoomInfo.word_sources.length == 0) {
        this.$message({type: 'warning', message: '请选择至少一个词库源', duration: 1000})
        return
      }

      this.$http({
        method: 'POST',
        url: '/api/create_room',
        data: {
          hostRoomInfo: _this.hostRoomInfo,
        },
      })
        .then((res) => {
          console.log(res.data)
          if(res.data.code == 'success') {
            _this.$store.commit('setCurRoom', res.data.roomInfo)
            _this.$router.push('/room')
          }
        })
    },
    // 载入房间列表
    reloadRooms() {
      let _this = this
      this.$http({
        method: 'POST',
        url: '/api/list_rooms',
        data: {},
      })
        .then((res) => {
          console.log(res.data)
          if(res.data.code == 'success') {
            _this.roomList = res.data.rooms
          }
        })
        .catch((err) => {
          console.log(err)
        })
    },
    // 加入房间
    joinRoom(roomId) {
      let _this = this
      this.$http({
        method: 'POST',
        url: '/api/join_room',
        data: {roomId: roomId, password: ''},
      })
        .then((res) => {
          console.log(res.data)
          if(res.data.code == 'success') {
            _this.$store.commit('setCurRoom', res.data.roomInfo)
            _this.$router.push('/room')
          }
        })
        .catch((err) => {
          console.log(err)
        })
      console.log(roomId)
    },
  }
}
</script>

<style lang="scss" scoped>
* {
  box-sizing: border-box;
}
.roomTab {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  color: #fffe;
  text-shadow: 2px 2px 12px #000c;
  overflow: hidden;

  .roomTabHeader {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    border-bottom: solid 1px #fff3;

    .left {
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      align-items: center;
      p {
        font-size: 20px;
        margin: 5px;
      }
      span {
        margin-left: 5px;
        font-size: 14px;
      }
    }
  }

  .roomListWindow {
    width: 100%;
    flex: 1 0 auto;
    height: 0;
    overflow-y: scroll;
    overflow-x: hidden;
    left: 17px;
    position: relative;
    .roolList {
      width: 100%;
      
      padding: 8px 25px 5px 4px;
      box-sizing: border-box;

      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: flex-start;

      .room {
        border-radius: 18px;
        background-color: rgba(255, 222, 192, 0.253);
        border: 1px solid #fff4;
        box-shadow: #0003 4px 4px 16px;
        padding: 10px 16px;
        margin: 8px 0;
        height: 80px;
        width: 98%;
        position: relative;
        transition: all 0.3s;
        top: 0px;
        left: 3px;
  
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-start;
  
        .side {
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-items: flex-start;

          .room-name {
            font-size: 22px;
          }

          .player-num {
            color: #fdd;
            margin-left: 8px;
            border-left: solid 1px #fff;
            padding-left: 8px;
          }

          .el-icon-lock{
            color: rgb(255, 242, 0);
            margin-left: 8px;
            font-size: 20px
          }
        }
        .side:last-child {
          align-items: flex-end;
        }
      }

      .waiting {
        .side {
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-items: flex-start;

          .room-name {
            font-size: 22px;
          }

          .player-num {
            color: #cfc;
            margin-left: 8px;
            border-left: solid 1px #fff;
            padding-left: 8px;
          }

          .player-num-full {
            color: #fdd;
          }
        }
      }
  }


    .room:hover {
      background-color: rgba(255, 255, 255, 0.36);
      box-shadow: #0005 4px 4px 24px;
      top: -3px;
      left: 4px;
      scale: 1.02;
    }
  }

}
/* 新建房间弹窗 */
::v-deep .el-dialog {
  background: rgb(245 180 143 / 48%);;
  backdrop-filter: blur(2.5px);
  text-shadow: none;
  border-radius: 18px;

  .el-dialog__title {
    color: #fff;
    text-shadow: 2px 2px 12px #000c;
  }
  
  .row {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    text-shadow: 2px 2px 12px #000c;
    margin-bottom: 15px;

    span {
      flex: 0.27;
      color: #fff;
    }

    .el-input{
      flex: 0.75;
      color: #fff;

      .el-input__inner {
        color: #606266;
      }
    }

    .number-input {
      flex: 0.75;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      .icn {
        color: #fff80ebf;
        text-shadow: 0px 0px 3px #0008;
        font-size: 36px;
      }
    }
  }
}

.el-button {
  border-radius: 8px;
  position: relative;
  box-shadow: #0003 4px 4px 16px;
}
.el-button:hover {
  scale: 1.05;
}

</style>
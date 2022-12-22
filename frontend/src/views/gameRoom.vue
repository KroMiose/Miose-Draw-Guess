<template>
  <div class="container" v-loading="loading" element-loading-background="#8888">
    <viewHeader :panelTitle="'返回大厅'" @titleClick="exitRoom()"></viewHeader>
    <div class="viewContainer">
      <div class="viewBody">
        <boardTab :boardTitle="'玩家列表'" :ingameData="ingameData" :roomTitle="'聊天栏'" ref="boardTab" :syncFlag="syncFlag" class="boardTab" v-on:wsOnRecv="wsOnRecv"></boardTab>
        
        <div id="palette">
          <canvas id="canvas"
            class="cursor1"
            :width="canvasSize+'px'"
            :height="canvasSize+'px'"
          >您的浏览器不支持canvas画板，请尝试更换浏览器。</canvas>
        </div>
        <div class="toolBar">
          <i class="el-icon-refresh-left" @click="cancel()"></i>
          <el-color-picker
            v-model="color"
            show-alpha>
          </el-color-picker>
          <span v-text="penSize/10 + 'px'"></span>
          <el-slider
            v-model="penSize"
            vertical
            :step="1"
            :max="50"
            :min="10"
            :format-tooltip="formatTooltip"
            :show-tooltip="false"
            height="50px">
          </el-slider>
          <i :class="['el-icon-mobile-phone', eraserEnabled? 'active': '']" @click="eraserEnabled=!eraserEnabled"></i>
          <div :class="['colorBox', item == color? 'selected':'']" v-for="item in predefineColors" :key="item">
            <button :style="'background-color: ' + item" @click="setColor(item)"></button>
          </div>
          <i class="el-icon-delete" @click="clearCanves()"></i>
        </div>
      </div>
      <viewFoot></viewFoot>
      <div class="msgBoarderBox">
        {{showText}}
        <div class="optBtn">
          <el-button type="success" size="mini" @click="req_startGame()" v-show="getUsername == ingameData.hostname && gamestatus == 'waiting'">开始游戏</el-button>
          <el-button type="info" size="mini" @click="req_endRound(true)" v-show="getUsername == ingameData.curDrawer && gamestatus == 'drawing'">放弃绘图</el-button>
        </div>
      </div>
      <div :class="['wordSelectorBox', wordSelecting? 'wsb-show': 'wsb-hide']">
        <div class="wordSelectorTitle">请选择一个词语</div>
        <div class="wordSelector">
          <div class="wordItem" v-for="item in wordList" :key="item.word" v-text="item.word" @click="req_selectWord(item)"></div>
        </div>
      </div>
      <div class="timerBox">
        <div class="timer" v-text="timerText || '∞'"></div>
      </div>
    </div>
    <!-- 音效资源库 -->
    <div class="audiosrc" style="display:none">
      <audio id="got-answer" src="/audios/got_answer.mp3"></audio>
      <audio id="start-draw" src="/audios/start_draw.wav"></audio>
    </div>
  </div>
</template>

<script>
import viewHeader from '@/components/viewHeader.vue'
import viewFoot from '@/components/viewFoot.vue'
import boardTab from '@/components/boardTab.vue'

export default {
  components: {viewHeader, viewFoot, boardTab},
  mounted() {
    let username = window.sessionStorage.getItem('username')
    if(username) {
      this.$store.commit('setUsername', username)
    }
    // 画板自适应
    window.onresize=function(){  
      document.getElementById('canvas').style.height = '500px'
      document.getElementById('canvas').style.width = '500px'
      // 节流
      clearTimeout(this.resizeTimer)
      this.resizeTimer = setTimeout(() => {
        document.getElementById('canvas').style.height = document.getElementById('palette').scrollHeight + 'px'
        document.getElementById('canvas').style.width = document.getElementById('palette').scrollHeight + 'px'
      }, 300)
    } 
    setTimeout(() => {
      document.getElementById('canvas').style.height = document.getElementById('palette').scrollHeight + 'px'
      this.loading = false
    }, 500)

    this.loadCanvas()

    // 阶段倒计时定时器
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.timer = setInterval(() => {
      if(this.deadtimestamp) {
        let now = new Date().getTime()
        let diff = this.deadtimestamp - now
        if(diff > 0) {
          this.timerText = parseInt(diff / 1000) + 's'
        } else {
          this.timerText = ''
        }
      }
    }, 1000)
  },
  data() {
    return {
      loading: true,
      // wsUrl: 'ws://192.168.0.108:2910/draw_room',

      enableCanvasOpt: true,
      painting: false,
      eraserEnabled: false,
      startPoint: {x:0,y:0},
      ctx: null,
      canvas: null,
      canvasSize: 1000,
      color: '#000',
      penSize: 25,
      drawHistory: [],
      imagePath: [],
      drawPath: [],
      predefineColors: [
        '#000000',
        '#888888',
        '#ff4500',
        '#ff8c00',
        '#ffd700',
        '#90ee90',
        '#00ced1',
        '#1e90ff',
        '#b3a9ff',
      ],
      syncFlag: false,
      showText: '等待中: 自由绘画时间',
      gamestatus: 'waiting',
      wordSelecting: false,
      wordList: [],
      ingameData: {},
      deadtimestamp: 0,
      timerText: '',
    }
  },
  watch: {
    color: function(nv, ov) {
      this.ctx.strokeStyle = nv;
    }
  },
  computed: {
    getUsername() {
      return this.$store.state.username
    },
  },
  methods: {
    
    // 请求开始游戏
    req_startGame() {
      this.sendWsMsg({type: 'opt', commend: 'startGame'})
    },
    //  执行开始游戏
    run_startGame() {
      this.enableCanvasOpt = false  // 禁止画板操作
      this.$message({
        message: '游戏即将开始',
        type: 'success',
        duration: 1000
      });

      setTimeout(() => {
        if(this.getUsername == this.ingameData.hostname) {
          this.sendWsMsg({type: 'opt', commend: 'startRound'})
        }
      }, 1500);
    },
    // 执行选词流程
    run_selectWord() {
      this.$http({
        method: 'post',
        url: '/api/get_word',
        data: {
          source: this.ingameData.word_sources
        }
      })
        .then(res => {
          // 播放音效
          let audio = document.getElementById('start-draw')
          audio.volume = 0.8
          audio.play()
          this.wordList = res.data.data
          this.wordSelecting = true
          // this.$message({
          //   message: '现在是你的回合，请选择一个词语开始绘画',
          //   type: 'success'
          // });
          this.selectWordTimer = setTimeout(() => { // 超时选择随机词
            this.req_selectWord(this.wordList[Math.floor(Math.random() * this.wordList.length)])
          }, this.ingameData.selection_duration * 1000);
        })
    },

    // 提交选词
    req_selectWord(word) {
      if(this.selectWordTimer) {
        clearTimeout(this.selectWordTimer)
      }
      this.wordSelecting = false
      this.sendWsMsg({type: 'opt', commend: 'selectWord', word: word})
    },

    // 开始绘画
    run_startRound() {
      this.resetCanvas()  // 重置画板

      // 主持人设置回合结束计时器
      if(this.getUsername == this.ingameData.hostname) {
        this.roundTimer = setTimeout(() => {
          this.sendWsMsg({type: 'opt', commend: 'endRound'})
        }, this.ingameData.roundDuration * 1000);
      }

      if(this.ingameData.curDrawer === this.getUsername) {
        this.enableCanvasOpt = true
        // this.$message({
        //   message: '现在是你的回合，请开始绘画',
        //   type: 'success'
        // });
      } else {
        // this.$message({
        //   message: '现在是' + this.ingameData.curDrawer + '的回合，请等待',
        //   type: 'success'
        // });
      }
    },

    // 结束回合
    req_endRound() {
      this.sendWsMsg({type: 'opt', commend: 'endRound', is_give_up: true})
    },

    // 结束绘画
    run_endRound() {
      this.enableCanvasOpt = false
      this.deadtimestamp = 0
      if(this.roundTimer) {
        clearTimeout(this.roundTimer)
      }
      this.$message({
        message: '回合结束',
        type: 'success'
      });

      if(this.getUsername == this.ingameData.hostname) {
        if(this.roundTimer) {
          clearTimeout(this.roundTimer)
        }
        setTimeout(() => {
          this.sendWsMsg({type: 'opt', commend: 'startRound'})
        }, this.ingameData.commentDuration * 1000);
      }
    },

    // 更新分数
    run_updateScore() {
      // 播放音效
      let audio = document.getElementById('got-answer')
      audio.volume = 0.5
      audio.play()
    },

    // 主持人离线
    run_hostOffline() {
      this.$message({
        message: '主持人已离线，游戏结束',
        type: 'error',
        duration: 1500,
      })
      this.exitRoom()
    },
    
    // 接收到ws信息
    wsOnRecv(data) {
      // console.log('接收到ws信息', data)
      let _this = this
      if(data.type === 'path') {  // 处理绘图路径
        if(data.sender !== this.getUsername) {
          if(data.path.o) {
            if(data.path.o === 'clear') {
              this.clearCanves(true)
            } else if(data.path.o === 'cancel') {
              this.cancel(true)
            }
          } else if(data.path.e){
            data.path.l.forEach(function(pos){
              _this.eraseRaw(pos.x, pos.y)
            })
          } else{
            this.drawPathRaw(data.path.w, data.path.c, data.path.l)
            let image = this.ctx.getImageData(0, 0, this.canvasSize, this.canvasSize);
            this.drawHistory.push(image)
          }
        }
      } else if (data.type == "opt") {
        switch (data.runMethod) {
          case 'run_startGame': _this.run_startGame(); break;
          case 'run_selectWord': _this.run_selectWord(); break;
          case 'run_startRound': _this.run_startRound(); break;
          case 'run_endRound': _this.run_endRound(); break;
          case 'run_updateScore': _this.run_updateScore(); break;
          case 'run_hostOffline': _this.run_hostOffline(); break;
        
          default: break;
        }
      }
      if(data.showText) {
        this.showText = data.showText
      }
      if(data.ingameData) {
        data.ingameData.userlist.sort((x1, x2) => {
          return x2.score - x1.score
        })
        this.ingameData = data.ingameData
      }
      if(data.deadtimestamp) {
        this.deadtimestamp = data.deadtimestamp
      }
      if(data.setStatus) {
        this.gamestatus = data.setStatus
      }
      let is_host_online = false
      data.ingameData.userlist.forEach((user) => {
        if(user.username === data.ingameData.hostname) {
          is_host_online = true
        }
      })
      if(!is_host_online) {
        this.run_hostOffline()
      }
    },
    // 离开房间
    exitRoom() {
      this.sendWsMsg({type: 'opt', commend: 'exitRoom'})
      this.$router.push('/')
    },
    // 发送消息
    sendWsMsg(data) {
      // data = {sender:this.getUsername, timestamp, type:'path'}
      let timestamp = (new Date()).valueOf()
      data.sender = this.getUsername
      data.timestamp = timestamp
      this.$refs.boardTab.submitPath(JSON.stringify(data))
    },
    // 绘画步骤完成触发
    drawStep(opt) {
      if(opt === true) return
      // console.log('更新画板')
      let timestamp = (new Date()).valueOf();
      if(opt){
        this.imagePath.push({
          o: opt
        })
      } else {
        this.imagePath.push({
          w:this.ctx.lineWidth,
          c:this.ctx.strokeStyle,
          l:this.drawPath,
          e:this.eraserEnabled,
        })
      }
      this.drawPath = []
      let curPathStr = JSON.stringify({sender:this.getUsername, path:this.imagePath[this.imagePath.length-1], timestamp, type:'path'})
      // console.log(this.imagePath)
      this.$refs.boardTab.submitPath(curPathStr)
    },
    // 加载画板
    loadCanvas() {
      let _this = this
      // 获取画板和画笔上下文
      _this.canvas = document.getElementById('canvas');
      _this.ctx = canvas.getContext('2d');

      //笔画颜色
      _this.ctx.strokeStyle = _this.color;
      //线宽
      _this.ctx.lineWidth = 2;
      _this.clearCanves()

      if (document.body.ontouchstart !== undefined) {
        _this.$message({type: 'info', message:'您正在使用支持触屏的设备进行游戏', duration: 2000})
      }else{
        _this.$message({type: 'info', message:'您正在使用不支持触屏的设备进行游戏', duration: 2000})
      }

      // 非触屏设备
      //鼠标点击事件（onmousedown）
      _this.canvas.onmousedown = function (e) {
        if(_this.enableCanvasOpt) {
          let x = e.offsetX;
          let y = e.offsetY;
          _this.painting = true;
          if (_this.eraserEnabled) {
            _this.drawPath.push({
              x: x / _this.calScaleRate(),
              y: y / _this.calScaleRate(),
              c: true
            })
            _this.erase(x, y)
            // _this.ctx.clearRect(x - 15, y - 15, 30, 30)
          }
          _this.startPoint = {x: x, y: y};
        }
      };
      // 鼠标滑动事件（onmousemove）
      _this.canvas.onmousemove = function (e) {
        if(_this.enableCanvasOpt) {
          let x = e.offsetX;
          let y = e.offsetY;
          let newPoint = {x: x, y: y};
          if (_this.painting) {
            if (_this.eraserEnabled) {
              _this.drawPath.push({
                x: x / _this.calScaleRate(),
                y: y / _this.calScaleRate(),
                c: true
              })
              _this.erase(x, y)
              // _this.ctx.clearRect(x - 15, y - 15, 30, 30)
            } else {
              _this.drawLine(_this.startPoint.x, _this.startPoint.y, newPoint.x, newPoint.y);
            }
            _this.startPoint = newPoint;
          }
        }
      };
      // 鼠标松开事件（onmouseup)
      _this.canvas.onmouseup = function () {
        if(_this.enableCanvasOpt) {
          _this.painting = false;
          let image = _this.ctx.getImageData(0, 0, _this.canvasSize, _this.canvasSize);
          _this.drawHistory.push(image);
          _this.drawStep()
        }
      };
      // 触屏设备
      // 触摸开始事件（ontouchstart）
      _this.canvas.ontouchstart = function (e) {
        if(_this.enableCanvasOpt) {
          let pos = _this.canvas.getBoundingClientRect()
          //[0]表示touch第一个触碰点
          let x = e.touches[0].clientX-pos.left;
          let y = e.touches[0].clientY-pos.top;
          _this.painting = true;
          if (_this.eraserEnabled) {
            _this.erase(x, y)
          }
          _this.startPoint = {x: x, y: y};
        }
      };
      // 触摸滑动事件（ontouchmove）
      _this.canvas.ontouchmove = function (e) {
        if(_this.enableCanvasOpt) {
          let pos = _this.canvas.getBoundingClientRect()
          let x = e.touches[0].clientX-pos.left;
          let y = e.touches[0].clientY-pos.top;
          let newPoint = {x: x, y: y};
          if (_this.painting) {
            if (_this.eraserEnabled) {
              _this.drawPath.push({
                x: x / _this.calScaleRate(),
                y: y / _this.calScaleRate(),
                c: true
              })
              _this.erase(x, y)
              // _this.ctx.clearRect(x - 15, y - 15, 30, 30)
            } else {
              _this.drawLine(_this.startPoint.x, _this.startPoint.y, newPoint.x, newPoint.y);
            }
            _this.startPoint = newPoint;
          }
        }
      };
      // 触摸结束事件（ontouchend）
      _this.canvas.ontouchend = function () {
        if(_this.enableCanvasOpt) {
          _this.painting = false;
          let image = _this.ctx.getImageData(0, 0, _this.canvasSize, _this.canvasSize);
          _this.drawHistory.push(image);
          _this.drawStep()
        }
      };
      // // 手写笔设备
      // // 手写笔开始事件（onpointerdown）
      // _this.canvas.onpointerdown = function (e) {
      //   if(_this.enableCanvasOpt) {
      //     let pos = _this.canvas.getBoundingClientRect()
      //     let x = e.clientX-pos.left;
      //     let y = e.clientY-pos.top;
      //     _this.painting = true;
      //     if (_this.eraserEnabled) {
      //       _this.erase(x, y)
      //     }
      //     _this.startPoint = {x: x, y: y};
      //   }
      // };
      // // 手写笔滑动事件（onpointermove）
      // _this.canvas.onpointermove = function (e) {
      //   if(_this.enableCanvasOpt) {
      //     let pos = _this.canvas.getBoundingClientRect()
      //     let x = e.clientX-pos.left;
      //     let y = e.clientY-pos.top;
      //     let newPoint = {x: x, y: y};
      //     if (_this.painting) {
      //       if (_this.eraserEnabled) {
      //         _this.erase(x, y)
      //       } else {
      //         _this.drawLine(_this.startPoint.x, _this.startPoint.y, newPoint.x, newPoint.y);
      //       }
      //       _this.startPoint = newPoint;
      //     }
      //   }
      // };
      // // 手写笔结束事件（onpointerup）
      // _this.canvas.onpointerup = function () {
      //   if(_this.enableCanvasOpt) {
      //     _this.painting = false;
      //     let image = _this.ctx.getImageData(0, 0, _this.canvasSize, _this.canvasSize);
      //     _this.drawHistory.push(image);
      //     _this.drawStep()
      //   }
      // };
    },
    // 设置画笔颜色
    setColor(color) {
      this.ctx.strokeStyle = color
      this.color = color
      this.eraserEnabled = false
    },
    // 计算缩放比例
    calScaleRate() {
      let cHeight = parseInt(document.getElementById('canvas').style.height.slice(0, -2))
      return cHeight / this.canvasSize
    },
    // 绘制线条
    drawLine(xStart, yStart, xEnd, yEnd) {
      let scaleRate = this.calScaleRate()
      let x1 = xStart / scaleRate
      let y1 = yStart / scaleRate
      let x2 = xEnd / scaleRate
      let y2 = yEnd / scaleRate
      this.drawPath.push({x1, y1, x2, y2})
      //开始绘制路径
      this.ctx.beginPath();
      //线宽
      this.ctx.lineWidth = this.penSize / 10;
      //起始位置
      this.ctx.moveTo(x1, y1);
      //停止位置
      this.ctx.lineTo(x2, y2);
      //描绘线路
      this.ctx.stroke();
      //结束绘制
      this.ctx.closePath();
    },
    // 绘制路径
    drawPathRaw(w, c, lineList) {
      let strokeStyleTmp = this.ctx.strokeStyle
      this.ctx.lineWidth = w
      this.ctx.strokeStyle = c
      let _this = this
      lineList.forEach(function (line){
        _this.drawLineRaw(line.x1, line.y1, line.x2, line.y2)
      })
      this.ctx.strokeStyle = strokeStyleTmp
    },
    // 绘制线条(绝对)
    drawLineRaw(x1, y1, x2, y2) {
      this.ctx.beginPath();
      this.ctx.moveTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.stroke();
      this.ctx.closePath();
    },
    // 撤回上一步 参数为真时忽略画板锁定且不广播此操作
    cancel(oby) {
      if(this.enableCanvasOpt || oby) {
        this.drawHistory.pop();
        if (this.drawHistory.length < 1) {
          this.clearCanves()
        } else {
          this.ctx.putImageData(this.drawHistory[this.drawHistory.length - 1], 0, 0);
          if(!oby)
            this.drawStep('cancel')
        }
      }
    },
    // 擦除
    erase(x, y) {
      let scaleRate = this.calScaleRate()
      this.ctx.clearRect(x / scaleRate - 20, y / scaleRate - 20, 40, 40)
    },
    // 擦除(绝对)
    eraseRaw(x, y) {
      this.ctx.clearRect(x - 20, y - 20, 40, 40)
    },
    // 清空画布 参数为真时忽略画板锁定且不广播此操作
    clearCanves(oby) {
      if(this.enableCanvasOpt || oby) {
        this.ctx.clearRect(0, 0, this.canvasSize, this.canvasSize);
        let image = this.ctx.getImageData(0, 0, this.canvasSize, this.canvasSize);
        this.drawHistory.push(image)
        if(!oby)
          this.drawStep('clear')
      }
    },
    // 格式化笔触大小像素显示
    formatTooltip(val) {
      return val / 10;
    },
    // 重置画板
    resetCanvas() {
      this.clearCanves(true)  // 清空画布
      this.drawHistory = []   // 清空历史记录
    },
  },
  beforeUnmount() {
    clearInterval(this.timer)
  }
}
</script>

<style lang="scss" scoped>
.container {
  width: 100%;
  height: 100%;
  overflow: hidden;

  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;

  box-shadow: 2px 2px 8px #000a;

  .viewContainer {
    width: 94vw;
    height: 92vh;

    border-radius: 28px 28px 0 0;
    padding: 8px 16px 0;
    background-color: #fff6;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;

    .viewBody {
      flex: 1;
      width: 100%;
      padding: 10px 10px 0;

      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: flex-start;
      
      .boardTab {
        height: 100%;
        flex: 1;
      }
    }
  }
}

* {
  box-sizing: border-box;
}

.viewBody {
  .toolBar {
    background-color: #fff8;
    margin-top: 10px;
    padding: 12px 5px;
    border-radius: 20px;
  
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;

    .el-color-picker {
      margin-bottom: 4px;
      overflow: hidden;
    }
    span {
      background-color: #ccc;
      color: #444;
      padding: 4px;
      width: 42px;
      border-radius: 8px;
      text-align: center;
      border: solid 1px #8883;
    }
    .el-slider {
      width: 30px;
      border-radius: 16px;
      border: solid 1px #8883;
      background-color: #ccc;
      padding: 14px 0;
      margin: 10px 0;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: center;
    }

    .el-color-picker__trigger {
      border: none;
    }
    .colorBox {
      display: block;
      box-sizing: border-box;
      border-radius: 5px;
      margin: 0 0 4px;
      padding: 0;
      height: 30px;
      width: 30px;
      overflow: hidden;

      button {
        display: block;
        width: 100%;
        height: 100%;
        border: none;
      }
    }
    .selected {
      border: #acf solid 2px;
    }

    i {
      width: 30px;
      height: 30px;
      color: #333;
      border: solid 1px #333;
      border-radius: 5px;
      font-size: 22px;
      line-height: 29px;
      text-align: center;
      margin-bottom: 5px;
    }
    i.active {
      color: #acf;
      border-color: #acf;
    }
  }

}

#palette {
  height: 100%;
  padding: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  
  #canvas {
    transition: all 0.2s;
    background-color: #fff;
    height: 300px;
    border: 2px solid rgba(255, 202, 96, 0.735);
    box-shadow: 0 0 12px #fff8;
    border-radius: 8px;
  }
}

.msgBoarderBox {
  position: fixed;
  left: 50%;
  top: -8px;
  margin-left: -25vw;
  width: 50vw;
  height: 48px;
  line-height: 50px;
  text-align: center;
  border-radius: 0 0 16px 16px;
  background-color: #fff;
  color: #e1ae99;
  font-size: 22px;
  border: 4px solid #FDB99B88;

  .optBtn {
    position: absolute;
    top: -2px;
    right: 0;
  }
}

.wordSelectorBox {
  position: fixed;
  left: 50%;
  top: 50%;
  margin-left: -20vw;
  margin-top: -25vh;
  width: 40vw;
  height: 20vh;
  border-radius: 16px;
  background-color: #fffa;
  color: #444;
  font-size: 22px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding: 10px 0 0;
  transition: all 0.3s;
  border: 1px solid #ffcfbb;
  overflow: hidden;
  box-shadow: #0003 4px 4px 16px;

  .wordSelectorTitle {
    width: 100%;
    text-align: center;
    line-height: 20px;
    font-size: 18px;
    color: #444;
    padding: 10px 0 10px;
    border-bottom: 1px solid #ffcfbb;
  }

  .wordSelector {
    flex: 1;
    width: 100%;
    padding: 0 10px;
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    flex-wrap: wrap;
    background-color: #0001;

    .wordItem {
      line-height: 30px;
      text-align: center;
      border-radius: 8px;
      margin: 4px;
      padding: 8px;
      background-color: #fff;
      color: #444;
      font-size: 18px;
      border: 1px solid #ffcfbb;
      box-shadow: #0003 2px 2px 8px;
      cursor: pointer;
    }
  }
}
.wsb-hide {
  top: -100vh;
}
.wsb-show {
  top: 50%;
}

.timerBox {
  position: fixed;
  left: 150px;
  top: 0;

  .timer {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: #fff;
    color: #666;
    font-size: 24px;
    line-height: 44px;
    text-align: center;
    border: 3px solid #ffcfbb;
    box-shadow: #0003 2px 2px 8px;
  }
}

</style>
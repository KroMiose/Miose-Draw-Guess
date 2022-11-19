<template>
  <div class="container" v-loading="loading" element-loading-background="#8888">
    <viewHeader :panelTitle="'游戏房间'"></viewHeader>
    <div class="viewContainer">
      <div class="viewBody">
        <boardTab :wsUrl="wsUrl" :boardTitle="'玩家列表'" :ingameData="ingameData" :roomTitle="'聊天栏'" ref="boardTab" :syncFlag="syncFlag" class="boardTab" v-on:wsOnRecv="wsOnRecv"></boardTab>
        
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
          <el-button @click="req_startGame()">开始游戏</el-button>
        </div>
      </div>
      <div :class="['wordSelectorBox', wordSelecting? 'wsb-show': 'wsb-hide']">
        <div class="wordSelector">
          <div class="wordSelectorTitle">请选择一个词语</div>
          <div class="wordSelectorBody">
            <div class="wordSelectorItem" v-for="item in wordList" :key="item.word" @click="req_selectWord(item)">
              <div class="wordSelectorItemText" v-text="item.word"></div>
            </div>
          </div>
        </div>
      </div>
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
    setTimeout(() => {
      document.getElementById('canvas').style.height = document.getElementById('palette').scrollHeight + 'px'
      this.loading = false
    }, 500)

    this.loadCanvas()
  },
  data() {
    return {
      loading: true,
      wsUrl: 'ws://192.168.0.108:2910/draw_room',

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
        // '#c71585',
      ],
      syncFlag: false,
      showText: '等待中...',
      wordSelecting: false,
      wordList: [],
      ingameData: {},
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
        type: 'success'
      });

      setTimeout(() => {
        if(this.ingameData.hostname == this.getUsername) {
          this.sendWsMsg({type: 'opt', commend: 'startRound'})
        }
      }, 1000);
    },
    // 执行选词流程
    run_selectWord() {
      this.$http({
        method: 'get',
        url: '/api/get_word',
      })
        .then(res => {
          this.wordList = res.data.data
          this.wordSelecting = true
          this.$message({
            message: '现在是你的回合，请选择一个词语开始绘画',
            type: 'success'
          });
        })
    },

    // 提交选词
    req_selectWord(word) {
      this.wordSelecting = false
      this.sendWsMsg({type: 'opt', commend: 'selectWord', word: word})
    },

    // 开始绘画
    run_startRound() {
      this.resetCanvas()  // 重置画板

      // 主持人设置回合结束计时器
      if(this.ingameData.hostname === this.getUsername) {
        this.roundTimer = setTimeout(() => {
          this.sendWsMsg({type: 'opt', commend: 'endRound'})
        }, 60000);
      }

      if(this.ingameData.curDrawer === this.getUsername) {
        this.enableCanvasOpt = true
        this.$message({
          message: '现在是你的回合，请开始绘画',
          type: 'success'
        });
      } else {
        this.$message({
          message: '现在是' + this.ingameData.curDrawer + '的回合，请等待',
          type: 'success'
        });
      }
    },

    // 结束绘画
    run_endRound() {
      this.enableCanvasOpt = false
      this.$message({
        message: '回合结束',
        type: 'success'
      });
      if(this.ingameData.hostname == this.getUsername) {
        if(this.roundTimer) {
          clearTimeout(this.roundTimer)
        }
        setTimeout(() => {
          this.sendWsMsg({type: 'opt', commend: 'startRound'})
        }, 10000);
      }
    },
    
    // 接收到ws信息
    wsOnRecv(data) {
      console.log('接收到ws信息', data)
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
        
          default: break;
        }

        if(data.showText) {
          this.showText = data.showText
        }
        if(data.ingameData) {
          this.ingameData = data.ingameData
        }
      }
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
      console.log('更新画板')
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
      this.ctx.lineWidth = w
      this.ctx.strokeStyle = c
      let _this = this
      lineList.forEach(function (line){
        _this.drawLineRaw(line.x1, line.y1, line.x2, line.y2)
      })
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
    transition: all 0.5s;
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
  color: #ffcfbb;
  font-size: 22px;
  border: 4px solid #FDB99B88;
}

.wordSelectorBox {
  position: fixed;
  left: 50%;
  top: 50%;
  margin-left: -20vw;
  margin-top: -25vh;
  width: 40vw;
  height: 30vh;
  border-radius: 16px;
  background-color: #fffa;
  color: #444;
  font-size: 22px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding: 10px 0;
  transition: all 0.3s;
  border: 1px solid #ffcfbb;
  box-shadow: #0003 4px 4px 16px;

  .wordSelector {
    flex: 1;
    width: 100%;
    overflow: auto;
    padding: 0 10px;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: flex-start;
    flex-wrap: wrap;

    .wordItem {
      border: 1px solid #ffcfbb;
      padding: 4px;
      height: 30px;
      line-height: 30px;
      text-align: center;
      border-radius: 8px;
      background-color: #fff8;
      margin: 5px;
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

</style>
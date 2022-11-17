<template>
  <div class="viewHeader">
    <div class="left">
      <p v-text="panelTitle"></p>
    </div>
    <div class="right">
      <span @click="logout()" class="userinfo">欢迎 {{getUsername}}</span>
      <i @click="fullscreen()" class="el-icon-full-screen"></i>
    </div>
  </div>
</template>

<script>

export default {
  props: {
    panelTitle: String,
  },
  computed: {
    getUsername() {
      return this.$store.state.username
    },
  },
  methods: {
    fullscreen() {
    // 需要全屏显示的dom元素
      let dom = this.$el.querySelector('#app')
      // 调用全屏方法
      this.$fullscreen.enter(dom, {
        wrap: false,
        callback: f => {
          this.fullscreenFlag = f
        }
      })    
    },
    logout() {
      let _this = this
      this.$http({
        method: 'GET',
        url: '/api/logout',
      })
        .then(function() {
          console.log('登出成功')
          window.sessionStorage.removeItem('username')
          _this.$router.push('/login')
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.viewHeader {
  height: 50px;
  padding: 10px 24px;
  width: 100%;
  position: fixed;
  top: 0;
  left: 50%;
  margin-left: -50%;
  box-sizing: border-box;

  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;

  background: #ffffff40;  /* fallback for old browsers */
  background: -webkit-linear-gradient(to bottom, #0003, #0000);  /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to bottom, #0003, #0000); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */

  text-shadow: 2px 2px 8px #0008;

  .left {
    p {
      color: #fff;
      font-size: 24px;
    }
  }

  .right {
    .userinfo {
      font-size: 18px;
      color: #fff;
    }

    i {
      font-size: 18px;
      padding: 5px;
      margin-left: 10px;
      border-radius: 25%;
      background-color: #fff6;
    }
  }

}
</style>

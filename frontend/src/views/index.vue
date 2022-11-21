<template>
  <div class="container" v-loading="loading" element-loading-background="#8888">
    <viewHeader :panelTitle="'返回登录'" @titleClick="exitPubRoom()"></viewHeader>
    <div class="viewContainer">
      <div class="viewBody">
        <roomTab class="roomTab"></roomTab>
        <boardTab :boardTitle="'公告板'" :roomTitle="'公共频道'"></boardTab>
      </div>
      <viewFoot></viewFoot>
    </div>
  </div>
</template>

<script>
import viewHeader from '@/components/viewHeader.vue'
import viewFoot from '@/components/viewFoot.vue'
import roomTab from '@/components/roomTab.vue'
import boardTab from '@/components/boardTab.vue'

export default {
  components: {viewHeader, viewFoot, roomTab, boardTab},
  mounted() {
    let username = window.sessionStorage.getItem('username')
    if(username) {
      this.$store.commit('setUsername', username)
    }
    setTimeout(() => {this.loading = false}, 500)
  },
  data() {
    return {
      loading: true,
    }
  },
  methods: {
    exitPubRoom() {
      this.$router.push('/login')
    }
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
    width: 96vw;
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

      .roomTab {
        height: 100%;
        flex: 0.55;
        border-right: 1px solid #eeea;
      }
      
      .boardTab {
        height: 100%;
        flex: 0.45;
      }
    }
  }
}

* {
  box-sizing: border-box;
}

</style>
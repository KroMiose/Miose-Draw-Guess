<template>
  <div class="boardTab">
    <p class="panelTitle" v-text="boardTitle"></p>
    <div class="userlistContainer bulletinBoard" v-if="ingameData && ingameData.userlist">
      <div v-for="user in ingameData.userlist" :class="['user', user.got_answer? 'u-got':'', ingameData.curDrawer == user.username? 'u-drawer':'']" :key="user.username">
        <div class="username" v-text="user.username"></div>
        <div class="score" v-text="user.score"></div>
      </div>
    </div>
    <div class="bulletinBoard" v-else>

    </div>
    <p class="panelTitle" v-text="roomTitle"></p>
    <chatBoard ref="chatBoard" :syncFlag="syncFlag"  v-on:wsOnRecv="wsOnRecv"></chatBoard>
  </div>
</template>

<script>
import chatBoard from '@/components/chatBoard.vue'

export default {
  components: {chatBoard},
  props: {
    wsUrl: String,
    boardTitle: String,
    roomTitle: String,
    syncFlag: Boolean,
    ingameData: Object,
  },
  data() {
    return {

    }
  },
  computed: {
    getUsername() {
      return this.$store.state.username
    },
  },
  mounted() {

  },
  methods: {
    submitPath(data) {
      this.$refs.chatBoard.submitPath(data)
    },
    wsOnRecv(data) {
      this.$emit('wsOnRecv', data)
    },
  }
}
</script>

<style lang="scss" scoped>
* {
  box-sizing: border-box;
}

.boardTab {
  widows: 100%;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;

  .panelTitle {
    text-shadow: 2px 2px 8px #000c;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    text-align: left;
    margin: 12px 6px 4px;
  }

  .bulletinBoard {
    padding: 20px;
    text-shadow: 2px 2px 12px #000c;
    color: #fff;
    flex: 0.2;
    width: 100%;
    background-color: #fff3;
    box-shadow: #0003 4px 4px 16px;
    border-radius: 18px;
    overflow: hidden;
  }

  .userlistContainer {
    .user {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      margin: 4px 0;
      padding: 4px 8px;
      border-radius: 8px;
      background-color: #fff3;
      box-shadow: #0003 4px 4px 16px;
      width: 100%;
      height: 32px;

      .username {
        color: #fff;
        text-shadow: 2px 2px 12px #000c;
        margin-bottom: 5px;
      }
      .score {
        color: #fff;
        text-shadow: 2px 2px 12px #000c;
        margin-bottom: 5px;
      }
    }
    .u-got {
      background-color: #3f33;
    }
    .u-drawer {
      background-color: #ff33;
    }
  }
}
</style>
<template>
  <div class="boardTab">
    <p class="panelTitle" v-text="boardTitle"></p>
    <div class="bulletinBoard">

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
}
</style>
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    username: '游客',
    curRoom: {},
  },
  getters: {
  },
  mutations: {
    setUsername(state, username) {
      state.username = username
    },
    setCurRoom(state, curRoom) {
      state.curRoom = JSON.parse(JSON.stringify(curRoom))
    }
  },
  actions: {
  },
  modules: {
  }
})

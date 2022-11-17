import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'


// 导入element-ui
import './plugins/element.js'

// 导入全局样式表
import '@/assets/css/global.scss'

// 引入全屏显示模块
import fullscreen from 'vue-fullscreen'
Vue.use(fullscreen)

// 导入axios
import axios from 'axios'
import VueAxios from 'vue-axios'
axios.defaults.withCredentials = true // 让axios请求携带cookie
Vue.prototype.$http = axios
Vue.use(VueAxios, axios)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

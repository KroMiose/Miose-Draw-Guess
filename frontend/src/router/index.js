import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'index',
    component: () => import(/* webpackChunkName: "main" */ '@/views/index.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "login" */ '@/views/login.vue')
  },
  {
    path: '/room',
    name: 'room',
    component: () => import(/* webpackChunkName: "room" */ '@/views/gameRoom.vue')
  },
]

const router = new VueRouter({
  routes
})

// 挂载路由导航守卫
router.beforeEach((to, from, next) => {
  // to 将要访问的路径
  // from 代表从哪个路径跳转而来
  // next 是一个函数，表示放行
  //    next()  放行    next('/login')  强制跳转
  if (to.path === '/login') return next()
  // 获取token
  let username = window.sessionStorage.getItem('username')
  if (!username) return next('/login')
  next()
})

export default router

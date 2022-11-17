import Vue from 'vue'
import ElementUI, { Button } from 'element-ui'
import { Form,FormItem } from 'element-ui'
import { Input } from 'element-ui'
import { Pagination } from 'element-ui'
import { Message } from 'element-ui'
import 'element-ui'


// 按需引入Vue组件
Vue.use(ElementUI)
Vue.use(Button)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Input)
Vue.use(Pagination)
Vue.prototype.$message = Message

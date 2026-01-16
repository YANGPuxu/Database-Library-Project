import { createApp } from 'vue'
import App from './App.vue' // 引入刚才改好的 App.vue

// 1. 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 2. 引入路由 (这就是刚才新建的那个文件)
import router from './router'

const app = createApp(App)

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router) // 👈 这一行最关键，没有它路由不生效
app.mount('#app')
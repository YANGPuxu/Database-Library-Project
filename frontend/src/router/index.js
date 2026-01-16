import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    // 这里默认跳转到读者管理，防止右边一片白
    redirect: '/home/readers',
    children: [
      {
        path: 'readers',
        name: 'ReaderManage',
        component: () => import('../views/ReaderManage.vue')
      },
      {
        path: 'books',
        name: 'BookManage',
        // 还没建，先用 ReaderManage 顶替一下防止报错，或者你可以马上建一个空文件
        // 建议马上建一个空的 BookManage.vue
        component: () => import('../views/BookManage.vue') 
      },
      {
        path: 'borrow',
        name: 'BorrowManage',
        component: () => import('../views/BorrowManage.vue')
      },
      {
        path: 'return',
        name: 'ReturnManage',
        component: () => import('../views/ReturnManage.vue')
      },
      {
        path: 'fines',
        name: 'FineManage',
        component: () => import('../views/FineManage.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
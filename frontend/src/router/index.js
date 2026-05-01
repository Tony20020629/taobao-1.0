import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/HomePage.vue')
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('../views/DataPage.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

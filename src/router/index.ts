import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api/http'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      // 认证页不显示导航栏
      meta: { hideNav: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { hideNav: true },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/HistoryView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// 全局前置守卫：未登录访问受保护页面跳转登录页（携带回跳地址）；
// 已登录访问认证页（登录/注册）直接回首页
router.beforeEach((to) => {
  const loggedIn = Boolean(getToken())
  if (to.meta.requiresAuth && !loggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (loggedIn && (to.path === '/login' || to.path === '/register')) {
    return { path: '/' }
  }
  return true
})

export default router

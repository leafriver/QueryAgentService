<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { useUserStore } from '@/stores/user'
import { AUTH_UNAUTHORIZED_EVENT } from '@/api/http'
import type { MenuItem, NavItem } from '@/types/navbar'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 认证页（登录/注册）不显示导航栏
const showNav = computed(() => !route.meta.hideNav)

onMounted(() => {
  // 启动时尝试恢复登录态（本地有令牌则向后端拉取用户信息）
  userStore.restoreSession()
  // 令牌失效（401）时清理登录态并跳转登录页
  window.addEventListener(AUTH_UNAUTHORIZED_EVENT, () => {
    userStore.clearSession()
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  })
})

const navItems: NavItem[] = [
  { key: 'home', label: '首页', path: '/' },
  { key: 'chat', label: '新对话', path: '/chat'},
  { key: 'history', label: '历史记录', path: '/history'},
]

const menuItems: MenuItem[] = [
  { key: 'profile', label: '个人信息', icon: '👤' },
  { key: 'history', label: '历史记录', icon: '🕘' },
  { key: 'settings', label: '设置', icon: '⚙️' },
  { key: 'logout', label: '退出登录', icon: '🚪', divided: true, danger: true },
]

function handleMenuSelect(key: string) {
  if (key === 'logout') {
    userStore.logout()
    router.push('/login')
    return
  }
  // 个人信息 / 历史记录 / 设置页面尚未创建，后续接入
  console.info('[NavBar] 菜单点击：', key)
}
</script>

<template>
  <NavBar
    v-if="showNav"
    :nav-items="navItems"
    :user="userStore.user"
    :menu-items="menuItems"
    @menu-select="handleMenuSelect"
  />
  <router-view />
</template>
<style>
*{
  margin: 0;
  padding: 0;
}
</style>
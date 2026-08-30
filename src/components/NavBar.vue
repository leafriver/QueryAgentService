<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from '@/utils/useTheme'
import type { MenuItem, NavItem, UserInfo } from '@/types/navbar'

const props = withDefaults(
  defineProps<{
    /** 导航项，由父组件传入 */
    navItems: NavItem[]
    /** 用户信息，null 表示未登录 */
    user?: UserInfo | null
    /** 用户下拉菜单项，由父组件传入 */
    menuItems?: MenuItem[]
    /** Logo 文字 */
    logoText?: string
    /** Logo 图片地址，存在时优先展示 */
    logoImage?: string
    /** 点击 Logo 跳转的路径 */
    homePath?: string
    /** 未登录时点击跳转的登录页路径 */
    loginPath?: string
  }>(),
  {
    user: null,
    menuItems: () => [],
    logoText: 'QueryAgent',
    logoImage: '',
    homePath: '/',
    loginPath: '/login',
  },
)

const emit = defineEmits<{
  /** 点击导航项 */
  navigate: [item: NavItem]
  /** 点击下拉菜单项 */
  menuSelect: [key: string, item: MenuItem]
  /** 点击未登录按钮 */
  login: []
}>()

const router = useRouter()
const route = useRoute()
const { theme, toggleTheme } = useTheme()

const menuOpen = ref(false)
let hideTimer: ReturnType<typeof setTimeout> | undefined

const isLogin = computed(() => Boolean(props.user))

/** 头像缺省时展示的文字（用户名首字符） */
const avatarText = computed(() => {
  const name = props.user?.name?.trim()
  return name ? name.charAt(0).toUpperCase() : '?'
})

const logoInitial = computed(() => props.logoText.trim().charAt(0).toUpperCase())

function clearHideTimer() {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = undefined
  }
}

function openMenu() {
  clearHideTimer()
  menuOpen.value = true
}

/** 延迟关闭，避免鼠标在头像与菜单之间移动时菜单闪断 */
function closeMenu(delay = 160) {
  clearHideTimer()
  hideTimer = setTimeout(() => {
    menuOpen.value = false
  }, delay)
}

function toggleMenu() {
  menuOpen.value ? closeMenu(0) : openMenu()
}

function isActive(item: NavItem) {
  if (item.active !== undefined) return item.active
  if (!item.path) return false
  return item.path === '/' ? route.path === '/' : route.path.startsWith(item.path)
}

function handleNavClick(item: NavItem) {
  if (item.disabled) return
  emit('navigate', item)
  if (item.path) router.push(item.path)
}

function handleMenuSelect(item: MenuItem) {
  emit('menuSelect', item.key, item)
  if (item.path) router.push(item.path)
  closeMenu(0)
}

function handleLogin() {
  emit('login')
  router.push(props.loginPath)
}

function handleLogo() {
  if (props.homePath) router.push(props.homePath)
}

onBeforeUnmount(clearHideTimer)
</script>

<template>
  <header class="navbar">
    <div class="navbar__inner">
      <!-- 左侧 Logo -->
      <a class="navbar__logo" @click="handleLogo">
        <img v-if="logoImage" class="navbar__logo-img" :src="logoImage" :alt="logoText" />
        <span v-else class="navbar__logo-mark">{{ logoInitial }}</span>
        <span class="navbar__logo-text">{{ logoText }}</span>
      </a>

      <!-- 中间导航项 -->
      <nav class="navbar__nav">
        <a
          v-for="item in navItems"
          :key="item.key ?? item.path ?? item.label"
          class="navbar__item"
          :class="{ 'is-active': isActive(item), 'is-disabled': item.disabled }"
          @click="handleNavClick(item)"
        >
          <span v-if="item.icon" class="navbar__icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </a>
      </nav>

      <!-- 右侧操作区：主题切换 + 登录状态 -->
      <div class="navbar__actions">
        <button
          class="navbar__theme"
          type="button"
          :title="theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'"
          @click="toggleTheme"
        >
          <Transition name="theme-icon" mode="out-in">
            <svg
              v-if="theme === 'dark'"
              key="sun"
              class="navbar__theme-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
            </svg>
            <svg
              v-else
              key="moon"
              class="navbar__theme-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </Transition>
        </button>

        <div class="navbar__user" @mouseenter="openMenu" @mouseleave="closeMenu()">
          <template v-if="isLogin && user">
            <button class="navbar__user-btn" type="button" @click="toggleMenu">
              <img v-if="user.avatar" class="navbar__avatar" :src="user.avatar" :alt="user.name" />
              <span v-else class="navbar__avatar navbar__avatar--text">{{ avatarText }}</span>
              <span class="navbar__user-name">{{ user.name }}</span>
              <span class="navbar__caret" :class="{ 'is-open': menuOpen }">▾</span>
            </button>

            <Transition name="navbar-dropdown">
              <div v-if="menuOpen && menuItems.length" class="navbar__dropdown">
                <div class="navbar__dropdown-head">
                  <p class="navbar__dropdown-name">{{ user.name }}</p>
                  <p v-if="user.email" class="navbar__dropdown-email">{{ user.email }}</p>
                </div>

                <template v-for="item in menuItems" :key="item.key">
                  <div v-if="item.divided" class="navbar__divider" />
                  <button
                    class="navbar__dropdown-item"
                    :class="{ 'is-danger': item.danger }"
                    type="button"
                    @click="handleMenuSelect(item)"
                  >
                    <span v-if="item.icon" class="navbar__icon">{{ item.icon }}</span>
                    <span>{{ item.label }}</span>
                  </button>
                </template>
              </div>
            </Transition>
          </template>

          <button v-else class="navbar__login" type="button" @click="handleLogin">未登录</button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition-theme);
}

.navbar__inner {
  display: flex;
  align-items: center;
  gap: 24px;
  height: 56px;
  padding: 0 24px;
}

/* ---------- Logo ---------- */
.navbar__logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
}

.navbar__logo-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.navbar__logo-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-inverse);
  background-color: var(--color-primary);
  border-radius: var(--radius-md);
}

.navbar__logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

/* ---------- 导航项 ---------- */
.navbar__nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
}

.navbar__item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-theme);
}

.navbar__item:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.navbar__item.is-active {
  color: var(--color-primary);
  background-color: var(--color-primary-soft);
  font-weight: 500;
}

.navbar__item.is-disabled {
  color: var(--text-muted);
  cursor: not-allowed;
  pointer-events: none;
}

.navbar__icon {
  font-size: 14px;
  line-height: 1;
}

/* ---------- 右侧操作区 ---------- */
.navbar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.navbar__theme {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: var(--text-secondary);
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: var(--transition-theme);
}

.navbar__theme:hover {
  color: var(--color-primary);
  background-color: var(--bg-hover);
  border-color: var(--border-color);
}

.navbar__theme-icon {
  width: 18px;
  height: 18px;
}

/* 主题图标切换动画 */
.theme-icon-enter-active,
.theme-icon-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.theme-icon-enter-from {
  opacity: 0;
  transform: rotate(-60deg) scale(0.7);
}

.theme-icon-leave-to {
  opacity: 0;
  transform: rotate(60deg) scale(0.7);
}

/* ---------- 用户区 ---------- */
.navbar__user {
  position: relative;
  display: flex;
  align-items: center;
}

.navbar__user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: var(--transition-theme);
}

.navbar__user-btn:hover {
  background-color: var(--bg-hover);
  border-color: var(--border-color);
}

.navbar__avatar {
  width: 28px;
  height: 28px;
  object-fit: cover;
  border-radius: var(--radius-full);
}

.navbar__avatar--text {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-inverse);
  background-color: var(--color-primary);
}

.navbar__user-name {
  max-width: 120px;
  overflow: hidden;
  font-size: 14px;
  color: var(--text-primary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.navbar__caret {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform 0.2s ease;
}

.navbar__caret.is-open {
  transform: rotate(180deg);
}

.navbar__login {
  padding: 6px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: var(--transition-theme);
}

.navbar__login:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

/* ---------- 下拉菜单 ---------- */
.navbar__dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 100;
  min-width: 180px;
  padding: 6px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}

/* 顶部小箭头 */
.navbar__dropdown::before {
  content: '';
  position: absolute;
  top: -5px;
  right: 18px;
  width: 8px;
  height: 8px;
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  border-left: 1px solid var(--border-color);
  transform: rotate(45deg);
}

.navbar__dropdown-head {
  padding: 8px 10px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--border-color-light);
}

.navbar__dropdown-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.navbar__dropdown-email {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.navbar__dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  font-size: 14px;
  color: var(--text-primary);
  text-align: left;
  background-color: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-theme);
}

.navbar__dropdown-item:hover {
  background-color: var(--bg-hover);
}

.navbar__dropdown-item.is-danger {
  color: var(--color-danger);
}

.navbar__dropdown-item.is-danger:hover {
  background-color: rgba(220, 38, 38, 0.1);
}

.navbar__divider {
  height: 1px;
  margin: 4px 6px;
  background-color: var(--border-color-light);
}

/* 下拉动画 */
.navbar-dropdown-enter-active,
.navbar-dropdown-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.navbar-dropdown-enter-from,
.navbar-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>

import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo } from '@/types/navbar'

/** 已注册用户列表（localStorage） */
const REGISTERED_KEY = 'query-agent-users'
/** 当前登录用户（localStorage） */
const SESSION_KEY = 'query-agent-session'

/** 内置演示账号，便于未注册时直接体验登录 */
const DEMO_USER = { username: 'admin', password: 'admin123' }

interface RegisterPayload {
  username: string
  phone: string
  password: string
}

interface LoginPayload {
  username: string
  password: string
}

interface RegisteredUser extends RegisterPayload {}

function delay(ms = 600) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readRegistered(): RegisteredUser[] {
  try {
    const raw = localStorage.getItem(REGISTERED_KEY)
    return raw ? (JSON.parse(raw) as RegisteredUser[]) : []
  } catch {
    return []
  }
}

function writeRegistered(list: RegisteredUser[]) {
  localStorage.setItem(REGISTERED_KEY, JSON.stringify(list))
}

function readSession(): UserInfo | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  // 刷新页面后从 localStorage 恢复登录态
  const user = ref<UserInfo | null>(readSession())

  function persist() {
    if (user.value) {
      localStorage.setItem(SESSION_KEY, JSON.stringify(user.value))
    } else {
      localStorage.removeItem(SESSION_KEY)
    }
  }

  /** 登录（模拟请求）：匹配已注册用户或内置演示账号 */
  async function login(payload: LoginPayload): Promise<UserInfo> {
    await delay()

    const username = payload.username.trim()
    const registered = readRegistered()
    const matched = registered.find(
      (r) => r.username === username && r.password === payload.password,
    )

    if (!matched && !(username === DEMO_USER.username && payload.password === DEMO_USER.password)) {
      throw new Error('用户名或密码错误')
    }

    user.value = { name: username }
    persist()
    return user.value
  }

  /** 注册（模拟请求）：用户名唯一，成功后写入本地注册列表 */
  async function register(payload: RegisterPayload): Promise<void> {
    await delay()

    const username = payload.username.trim()
    const registered = readRegistered()

    if (registered.some((r) => r.username === username)) {
      throw new Error('用户名已存在，请更换一个')
    }

    writeRegistered([...registered, { ...payload, username }])
  }

  /** 退出登录 */
  function logout() {
    user.value = null
    persist()
  }

  return { user, login, register, logout }
})

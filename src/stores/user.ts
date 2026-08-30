import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo } from '@/types/navbar'
import { getMe, login as loginApi, register as registerApi } from '@/api/auth'
import type { LoginPayload, RegisterPayload, UserPayload } from '@/api/auth'
import { getToken, setToken } from '@/api/http'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)

  /** 将后端用户信息映射为前端 UserInfo */
  function toUserInfo(payload: UserPayload): UserInfo {
    return { id: payload.id, name: payload.username, email: payload.email }
  }

  /** 登录：调用后端接口获取 JWT，保存令牌后拉取用户信息 */
  async function login(payload: LoginPayload): Promise<UserInfo> {
    const { access_token } = await loginApi(payload)
    setToken(access_token)
    const info = await getMe()
    user.value = toUserInfo(info)
    return user.value
  }

  /** 注册：调用后端注册接口，成功后由页面跳转登录页并预填用户名 */
  async function register(payload: RegisterPayload): Promise<void> {
    await registerApi(payload)
  }

  /** 拉取当前登录用户信息，无令牌直接返回 null */
  async function fetchUser(): Promise<UserInfo | null> {
    if (!getToken()) return null
    const info = await getMe()
    user.value = toUserInfo(info)
    return user.value
  }

  /** 应用初始化时恢复登录态：令牌无效时清理本地状态并返回 null */
  async function restoreSession(): Promise<UserInfo | null> {
    if (!getToken()) return null
    try {
      return await fetchUser()
    } catch {
      setToken(null)
      user.value = null
      return null
    }
  }

  /** 退出登录：清除令牌与用户信息（后端 JWT 无状态，前端清理即可） */
  function logout() {
    setToken(null)
    user.value = null
  }

  /** 令牌失效时清理本地登录态（由 auth:unauthorized 事件触发） */
  function clearSession() {
    user.value = null
  }

  return { user, login, register, logout, fetchUser, restoreSession, clearSession }
})

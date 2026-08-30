import axios, { AxiosError } from 'axios'

/** 认证令牌的 localStorage 存储键 */
export const TOKEN_KEY = 'query-agent-token'

/** 读取本地保存的令牌 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/** 保存或清除令牌 */
export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

/** 后端统一错误响应体 */
interface ApiErrorBody {
  detail?: string | { msg?: string }[]
}

/**
 * 从任意错误中提取可展示的消息：
 * - 后端 FastAPI 错误体为 { detail: string }，直接取出
 * - 参数校验错误时 detail 为数组，取第一条 msg
 * - 网络错误 / 超时给出友好提示
 */
export function extractErrorMessage(error: unknown, fallback = '请求失败，请稍后重试'): string {
  if (axios.isAxiosError(error)) {
    const err = error as AxiosError<ApiErrorBody>
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
    if (err.response?.status === 401) return '用户名或密码错误'
    if (err.response?.status === 404) return '请求的接口不存在'
    if (err.code === 'ERR_NETWORK') return '无法连接服务器，请确认后端服务已启动'
    if (err.code === 'ECONNABORTED') return '请求超时，请稍后重试'
  }
  return fallback
}

/** 登录失效事件：token 过期 / 被拒绝时由拦截器派发，App 层监听并清理登录态 */
export const AUTH_UNAUTHORIZED_EVENT = 'auth:unauthorized'

/** axios 单例：baseURL 走 /api 前缀，由 Vite dev server 代理到后端 */
const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// 请求拦截器：自动注入 Bearer 令牌
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一处理 401（令牌失效）
http.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    const url = error.config?.url ?? ''
    // 登录接口 401 表示凭证错误，交由页面展示错误信息，不做跳转
    if (status === 401 && !url.includes('/auth/login')) {
      setToken(null)
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT))
    }
    return Promise.reject(error)
  },
)

export default http

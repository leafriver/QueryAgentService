import http from './http'

/** 登录请求参数（OAuth2 密码模式） */
export interface LoginPayload {
  username: string
  password: string
}

/** 注册请求参数 */
export interface RegisterPayload {
  username: string
  email: string
  password: string
}

/** 登录成功响应 */
export interface TokenResult {
  access_token: string
  token_type: string
}

/** 后端用户信息 */
export interface UserPayload {
  id: number
  username: string
  email: string
  created_at: string
}

/**
 * 登录：OAuth2 密码模式，请求体为 form-urlencoded 表单（不能用 JSON）
 * username 支持用户名或邮箱
 */
export async function login(payload: LoginPayload): Promise<TokenResult> {
  const form = new URLSearchParams()
  form.append('username', payload.username)
  form.append('password', payload.password)
  const { data } = await http.post<TokenResult>('/auth/login', form)
  return data
}

/** 注册：JSON 请求体，成功返回用户信息 */
export async function register(payload: RegisterPayload): Promise<UserPayload> {
  const { data } = await http.post<UserPayload>('/auth/register', payload)
  return data
}

/** 获取当前登录用户信息（需携带 Bearer 令牌） */
export async function getMe(): Promise<UserPayload> {
  const { data } = await http.get<UserPayload>('/auth/me')
  return data
}

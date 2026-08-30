/**
 * 表单校验工具（纯函数，供登录 / 注册页面复用）
 *
 * 校验契约统一为：`(value: string) => string | null`
 * - 返回错误文案表示校验不通过
 * - 返回 null 表示校验通过
 */

/** 统一校验函数签名 */
export type Validator = (value: string) => string | null

/** 校验用户名：必填、长度 3-20、只能包含字母/数字/下划线/中文 */
export function validateUsername(value: string): string | null {
  const v = value.trim()
  if (!v) return '请输入用户名'
  if (v.length < 3) return '用户名至少 3 个字符'
  if (v.length > 20) return '用户名不能超过 20 个字符'
  if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(v)) return '用户名只能包含字母、数字、下划线或中文'
  return null
}

/** 校验手机号：必填、11 位中国大陆手机号 */
export function validatePhone(value: string): string | null {
  const v = value.trim()
  if (!v) return '请输入手机号'
  if (!/^1[3-9]\d{9}$/.test(v)) return '手机号格式不正确'
  return null
}

/** 校验登录账号：必填，支持用户名或邮箱 */
export function validateLoginIdentifier(value: string): string | null {
  const v = value.trim()
  if (!v) return '请输入用户名或邮箱'
  if (v.length > 100) return '账号长度不能超过 100 个字符'
  return null
}

/** 校验邮箱：必填、标准邮箱格式 */
export function validateEmail(value: string): string | null {
  const v = value.trim()
  if (!v) return '请输入邮箱'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '邮箱格式不正确'
  return null
}

/** 校验密码：必填、长度 6-32 */
export function validatePassword(value: string): string | null {
  if (!value) return '请输入密码'
  if (value.length < 6) return '密码至少 6 位'
  if (value.length > 32) return '密码不能超过 32 位'
  return null
}

/** 校验确认密码：必填、与密码一致 */
export function validateConfirmPassword(password: string, confirm: string): string | null {
  if (!confirm) return '请再次输入密码'
  if (password !== confirm) return '两次输入的密码不一致'
  return null
}

/** 密码强度等级 */
export type PasswordLevel = 'low' | 'medium' | 'high'

/** 密码强度评估结果 */
export interface PasswordStrength {
  level: PasswordLevel
  score: number
}

/**
 * 评估密码强度，按长度、数字、字母、特殊字符组合打分（0-5）
 * - low（0-2 分）  medium（3-4 分）  high（5 分）
 */
export function checkPasswordStrength(value: string): PasswordStrength {
  if (!value) return { level: 'low', score: 0 }

  let score = 0
  const len = value.length

  if (len >= 6) score += 1
  if (len >= 10) score += 1
  if (/\d/.test(value)) score += 1
  if (/[a-zA-Z]/.test(value)) score += 1
  if (/[^a-zA-Z0-9]/.test(value)) score += 1

  const level: PasswordLevel = score >= 5 ? 'high' : score >= 3 ? 'medium' : 'low'
  return { level, score }
}

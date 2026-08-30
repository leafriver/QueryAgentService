/** 导航项 */
export interface NavItem {
  /** 显示文本 */
  label: string
  /** 路由路径，传入后点击自动跳转 */
  path?: string
  /** 唯一标识，未传 path 时用于区分每一项 */
  key?: string
  /** 前置图标，可传 emoji 或图标类名 */
  icon?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否高亮，不传则根据当前路由自动匹配 */
  active?: boolean
}

/** 登录用户信息，为 null 表示未登录 */
export interface UserInfo {
  /** 用户名 */
  name: string
  /** 头像地址，不传则使用用户名首字符 */
  avatar?: string
  /** 邮箱等附加信息，展示在下拉菜单头部 */
  email?: string
}

/** 用户下拉菜单项 */
export interface MenuItem {
  /** 菜单标识，如 profile / history / settings / logout */
  key: string
  /** 显示文本 */
  label: string
  /** 前置图标 */
  icon?: string
  /** 路由路径，传入后点击自动跳转 */
  path?: string
  /** 是否在上方显示分隔线 */
  divided?: boolean
  /** 是否为危险操作（如退出登录），显示为红色 */
  danger?: boolean
}

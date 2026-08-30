import { reactive } from 'vue'
import type { Validator } from './validators'

/**
 * 表单字段状态管理：统一处理「失焦后显示提示、输入时实时校验」的时机机制。
 *
 * 用法：
 *   const username = useField(validateUsername)
 *   模板：v-model="username.value"  @blur="username.markTouched()"
 *        v-if="username.showError"  {{ username.error }}
 */
export function useField(validate: Validator, initial = '') {
  const state = reactive({
    value: initial,
    touched: false,

    /** 错误文案，仅 touched 后返回（未触碰不显示错误） */
    get error(): string | null {
      return state.touched ? validate(state.value) : null
    },

    /** 是否展示错误提示 */
    get showError(): boolean {
      return state.error !== null
    },

    /** 标记字段已失焦，开始展示校验提示 */
    markTouched() {
      state.touched = true
    },

    /** 强制校验（用于提交时），返回错误文案或 null */
    validateNow(): string | null {
      state.touched = true
      return validate(state.value)
    },

    reset() {
      state.value = initial
      state.touched = false
    },
  })

  return state
}

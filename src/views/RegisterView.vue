<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useField } from '@/utils/useField'
import {
  checkPasswordStrength,
  validateConfirmPassword,
  validateEmail,
  validatePassword,
  validateUsername,
} from '@/utils/validators'

const router = useRouter()
const userStore = useUserStore()

const username = useField(validateUsername)
const email = useField(validateEmail)
const password = useField(validatePassword)
// 确认密码：实时依赖当前密码，密码变化时一致性校验同步更新
const confirmPassword = useField((value) => validateConfirmPassword(password.value, value))

const loading = ref(false)
const submitError = ref('')
const successMessage = ref('')

const strength = computed(() => checkPasswordStrength(password.value))

const strengthMeta = computed(() => {
  if (!password.value) return { label: '', level: '' as const, active: 0 }
  const activeMap = { low: 1, medium: 2, high: 3 } as const
  const labelMap = { low: '低', medium: '中', high: '高' } as const
  const level = strength.value.level
  return { label: labelMap[level], level, active: activeMap[level] }
})

const isSubmitting = computed(() => loading.value || Boolean(successMessage.value))

async function handleSubmit() {
  const error =
    username.validateNow() ??
    email.validateNow() ??
    password.validateNow() ??
    confirmPassword.validateNow()
  if (error) return

  loading.value = true
  submitError.value = ''
  try {
    await userStore.register({
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    successMessage.value = '注册成功，正在跳转到登录页…'
    setTimeout(() => {
      router.push({ path: '/login', query: { username: username.value.trim() } })
    }, 900)
  } catch (e) {
    submitError.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-glow auth-glow--one" />
    <div class="auth-glow auth-glow--two" />

    <div class="auth-card">
      <div class="auth-brand">
        <div class="auth-logo">Q</div>
        <h1 class="auth-title">注册</h1>
        <p class="auth-subtitle">创建账号，开启你的智能查询之旅</p>
      </div>

      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <div class="auth-field">
          <label class="auth-label" for="reg-username">用户名</label>
          <input
            id="reg-username"
            v-model="username.value"
            class="auth-input"
            :class="{ 'is-error': username.showError }"
            type="text"
            placeholder="3-20 个字符，支持中文、字母、数字"
            autocomplete="username"
            @blur="username.markTouched()"
          />
          <p v-if="username.showError" class="auth-error">{{ username.error }}</p>
        </div>

        <div class="auth-field">
          <label class="auth-label" for="reg-email">邮箱</label>
          <input
            id="reg-email"
            v-model="email.value"
            class="auth-input"
            :class="{ 'is-error': email.showError }"
            type="email"
            placeholder="请输入邮箱，用于账号找回"
            autocomplete="email"
            @blur="email.markTouched()"
          />
          <p v-if="email.showError" class="auth-error">{{ email.error }}</p>
        </div>

        <div class="auth-field">
          <label class="auth-label" for="reg-password">密码</label>
          <input
            id="reg-password"
            v-model="password.value"
            class="auth-input"
            :class="{ 'is-error': password.showError }"
            type="password"
            placeholder="请输入密码（6-32 位）"
            autocomplete="new-password"
            @blur="password.markTouched()"
          />
          <div class="strength">
            <div class="strength__bars">
              <span
                v-for="i in 3"
                :key="i"
                class="strength__bar"
                :class="i <= strengthMeta.active ? `is-${strengthMeta.level}` : ''"
              />
            </div>
            <span class="strength__text" :class="strengthMeta.level ? `is-${strengthMeta.level}` : ''">
              {{ strengthMeta.label ? `强度：${strengthMeta.label}` : '密码强度' }}
            </span>
          </div>
          <p v-if="password.showError" class="auth-error">{{ password.error }}</p>
        </div>

        <div class="auth-field">
          <label class="auth-label" for="reg-confirm">确认密码</label>
          <input
            id="reg-confirm"
            v-model="confirmPassword.value"
            class="auth-input"
            :class="{ 'is-error': confirmPassword.showError }"
            type="password"
            placeholder="请再次输入密码"
            autocomplete="new-password"
            @blur="confirmPassword.markTouched()"
          />
          <p v-if="confirmPassword.showError" class="auth-error">{{ confirmPassword.error }}</p>
        </div>

        <p v-if="submitError" class="auth-error auth-submit-error">{{ submitError }}</p>
        <p v-if="successMessage" class="auth-success">{{ successMessage }}</p>

        <button class="auth-submit" type="submit" :disabled="isSubmitting">
          <span>{{ loading ? '注册中…' : '注 册' }}</span>
          <span v-if="loading" class="auth-spinner" />
        </button>
      </form>

      <p class="auth-footer">
        已有账号？
        <RouterLink class="auth-link" to="/login">去登录</RouterLink>
      </p>
    </div>
  </div>
</template>

<style src="@/styles/auth.css"></style>

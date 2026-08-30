<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useField } from '@/utils/useField'
import { validateLoginIdentifier, validatePassword } from '@/utils/validators'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 注册成功后跳转登录页，预填用户名
const prefillUsername =
  typeof route.query.username === 'string' ? route.query.username : ''
// 被路由守卫拦截跳转时携带的回跳地址，登录成功后返回原目标页
const redirect =
  typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
    ? route.query.redirect
    : '/'

const username = useField(validateLoginIdentifier, prefillUsername)
const password = useField(validatePassword)

const loading = ref(false)
const submitError = ref('')

// 已登录用户访问登录页，直接回首页
onMounted(() => {
  if (userStore.user) router.replace('/')
})

async function handleSubmit() {
  const error = username.validateNow() ?? password.validateNow()
  if (error) return

  loading.value = true
  submitError.value = ''
  try {
    await userStore.login({
      username: username.value.trim(),
      password: password.value,
    })
    router.push(redirect)
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
        <h1 class="auth-title">登录</h1>
        <p class="auth-subtitle">欢迎回来，请登录你的账号</p>
      </div>

      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <div class="auth-field">
          <label class="auth-label" for="login-username">用户名 / 邮箱</label>
          <input
            id="login-username"
            v-model="username.value"
            class="auth-input"
            :class="{ 'is-error': username.showError }"
            type="text"
            placeholder="请输入用户名或邮箱"
            autocomplete="username"
            @blur="username.markTouched()"
          />
          <p v-if="username.showError" class="auth-error">{{ username.error }}</p>
        </div>

        <div class="auth-field">
          <label class="auth-label" for="login-password">密码</label>
          <input
            id="login-password"
            v-model="password.value"
            class="auth-input"
            :class="{ 'is-error': password.showError }"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            @blur="password.markTouched()"
          />
          <p v-if="password.showError" class="auth-error">{{ password.error }}</p>
        </div>

        <p v-if="submitError" class="auth-error auth-submit-error">{{ submitError }}</p>

        <button class="auth-submit" type="submit" :disabled="loading">
          <span>{{ loading ? '登录中…' : '登 录' }}</span>
          <span v-if="loading" class="auth-spinner" />
        </button>
      </form>

      <p class="auth-footer">
        还没有账号？
        <RouterLink class="auth-link" to="/register">立即注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<style src="@/styles/auth.css"></style>

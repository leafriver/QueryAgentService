<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<template>
  <div class="home">
    <section class="home__hero">
      <h1 class="home__title">
        {{ userStore.user ? `你好，${userStore.user.name}` : '你好，访客' }}
      </h1>
      <p class="home__subtitle">
        QueryAgentService —— 智能体驱动的数据查询服务平台
      </p>

      <template v-if="userStore.user">
        <p class="home__desc">你已登录，现在可以开始使用数据查询与智能体服务。</p>
        <button class="home__btn" type="button">开始查询</button>
      </template>
      <template v-else>
        <p class="home__desc">
          你还没有登录，登录后即可使用完整功能。
        </p>
        <div class="home__actions">
          <RouterLink class="home__btn" to="/login">登录</RouterLink>
          <RouterLink class="home__btn home__btn--ghost" to="/register">注册</RouterLink>
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 57px);
  min-height: calc(100dvh - 57px);
  padding: 24px;
  background:
    radial-gradient(ellipse at top left, var(--color-primary-soft), transparent 55%),
    var(--bg-primary);
  transition: var(--transition-theme);
}

.home__hero {
  max-width: 560px;
  text-align: center;
}

.home__title {
  margin: 0 0 12px;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
}

.home__subtitle {
  margin: 0 0 16px;
  font-size: 16px;
  color: var(--text-secondary);
}

.home__desc {
  margin: 0 0 24px;
  font-size: 14px;
  color: var(--text-muted);
}

.home__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.home__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 0 28px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-inverse);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.home__btn:hover {
  filter: brightness(1.06);
  box-shadow: 0 6px 16px var(--color-primary-soft);
  transform: translateY(-1px);
}

.home__btn--ghost {
  color: var(--color-primary);
  background: transparent;
  border: 1px solid var(--color-primary);
}

.home__btn--ghost:hover {
  background-color: var(--color-primary-soft);
  box-shadow: none;
}
</style>

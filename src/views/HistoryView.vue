<script setup lang="ts">
// “历史记录”占位页，后续完善历史对话列表功能
</script>

<template>
  <div class="history">
    <div class="history__hero">
      <h1 class="history__title">历史记录</h1>
      <p class="history__desc">功能开发中，敬请期待…</p>
    </div>
  </div>
</template>

<style scoped>
.history {
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

.history__hero {
  max-width: 560px;
  text-align: center;
}

.history__title {
  margin: 0 0 12px;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
}

.history__desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
}
</style>

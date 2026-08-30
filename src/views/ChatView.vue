<script setup lang="ts">
// “新对话”占位页，后续完善对话功能
</script>

<template>
  <div class="chat">
    <div class="chat__hero">
      <h1 class="chat__title">新对话</h1>
      <p class="chat__desc">功能开发中，敬请期待…</p>
    </div>
  </div>
</template>

<style scoped>
.chat {
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

.chat__hero {
  max-width: 560px;
  text-align: center;
}

.chat__title {
  margin: 0 0 12px;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
}

.chat__desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
}
</style>

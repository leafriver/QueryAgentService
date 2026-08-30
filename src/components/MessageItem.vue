<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { Message } from '@/api/chat'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps<{
  /** 消息内容；thinking / streaming 占位时可为空 */
  message?: Message
  /** 思考中占位（AI 侧三点动画） */
  thinking?: boolean
  /** 是否正在流式输出（内容末尾显示闪烁光标） */
  streaming?: boolean
}>()

const contentRef = ref<HTMLElement | null>(null)
let copyTimer: ReturnType<typeof setTimeout> | undefined

const isUser = computed(() => props.message?.role === 'user')
const html = computed(() => renderMarkdown(props.message?.content ?? ''))

/** 渲染完成后为代码块头部补充语言标签与复制按钮（已存在的跳过） */
async function decorateCodeBlocks() {
  await nextTick()
  const container = contentRef.value
  if (!container) return
  container.querySelectorAll('pre').forEach((pre) => {
    if (pre.querySelector('.msg-copy-btn')) return
    const code = pre.querySelector('code')
    const lang = code?.className.match(/language-(\w+)/)?.[1] ?? 'code'

    const header = document.createElement('div')
    header.className = 'msg-code-header'
    const label = document.createElement('span')
    label.className = 'msg-code-lang'
    label.textContent = lang
    const btn = document.createElement('button')
    btn.type = 'button'
    btn.className = 'msg-copy-btn'
    btn.textContent = '复制'
    btn.addEventListener('click', () => copyCode(pre))
    header.appendChild(label)
    header.appendChild(btn)
    pre.prepend(header)
  })
}

/** 复制代码块内容（优先 Clipboard API，失败时回退选中复制） */
async function copyCode(pre: HTMLElement) {
  const code = pre.querySelector('code')
  if (!code) return
  const text = code.textContent ?? ''
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const range = document.createRange()
    range.selectNodeContents(code)
    const selection = window.getSelection()
    selection?.removeAllRanges()
    selection?.addRange(range)
    document.execCommand('copy')
    selection?.removeAllRanges()
  }
  const btn = pre.querySelector<HTMLButtonElement>('.msg-copy-btn')
  if (btn) {
    btn.textContent = '已复制'
    if (copyTimer) clearTimeout(copyTimer)
    copyTimer = setTimeout(() => {
      if (btn.isConnected) btn.textContent = '复制'
    }, 1500)
  }
}

watch(html, decorateCodeBlocks)
onMounted(decorateCodeBlocks)
onBeforeUnmount(() => {
  if (copyTimer) clearTimeout(copyTimer)
})
</script>

<template>
  <div class="msg" :class="{ 'msg--user': isUser, 'msg--ai': !isUser }">
    <div class="msg__avatar" :class="{ 'msg__avatar--user': isUser }">
      <svg
        v-if="isUser"
        class="msg__avatar-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
      <svg
        v-else
        class="msg__avatar-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <rect x="4" y="4" width="16" height="16" rx="2" />
        <path d="M9 9h6M9 13h6M9 17h4" />
      </svg>
    </div>

    <div class="msg__body">
      <!-- 思考中占位气泡 -->
      <div v-if="thinking && !isUser" class="msg__bubble msg__bubble--ai msg__thinking">
        <span class="msg__thinking-dot" />
        <span class="msg__thinking-dot" />
        <span class="msg__thinking-dot" />
      </div>

      <div v-else class="msg__bubble" :class="isUser ? 'msg__bubble--user' : 'msg__bubble--ai'">
        <!-- AI 消息：Markdown 渲染 -->
        <div v-if="!isUser" ref="contentRef" class="msg__content" v-html="html" />
        <!-- 用户消息：纯文本保留换行 -->
        <div v-else class="msg__content msg__content--plain">{{ message?.content }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.msg {
  display: flex;
  gap: 12px;
  max-width: 100%;
}

.msg--user {
  flex-direction: row-reverse;
}

.msg__avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  margin-top: 4px;
  border-radius: var(--radius-md);
}

.msg__avatar--user {
  color: var(--text-inverse);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
}

.msg__avatar-icon {
  width: 18px;
  height: 18px;
}

.msg__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: min(720px, 100%);
  min-width: 0;
}

.msg__bubble {
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.7;
  overflow-wrap: break-word;
}

.msg__bubble--user {
  color: var(--text-inverse);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  border-radius: 16px 4px 16px 16px;
  align-self: flex-end;
}

.msg__bubble--ai {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color-light);
  border-radius: 4px 16px 16px 16px;
  align-self: flex-start;
}

.msg__content {
  min-width: 0;
}

.msg__content--plain {
  white-space: pre-wrap;
}

/* ---------- Markdown 内容样式 ---------- */
.msg__content :deep(p) {
  margin: 0 0 10px;
}

.msg__content :deep(p:last-child) {
  margin-bottom: 0;
}

.msg__content :deep(h1),
.msg__content :deep(h2),
.msg__content :deep(h3),
.msg__content :deep(h4) {
  margin: 14px 0 8px;
  line-height: 1.4;
}

.msg__content :deep(h1:first-child),
.msg__content :deep(h2:first-child),
.msg__content :deep(h3:first-child),
.msg__content :deep(h4:first-child) {
  margin-top: 0;
}

.msg__content :deep(ul),
.msg__content :deep(ol) {
  margin: 0 0 10px;
  padding-left: 22px;
}

.msg__content :deep(li) {
  margin: 3px 0;
}

.msg__content :deep(a) {
  color: var(--color-primary);
  text-decoration: underline;
}

.msg__content :deep(blockquote) {
  margin: 10px 0;
  padding: 6px 14px;
  color: var(--text-secondary);
  background-color: var(--bg-hover);
  border-left: 3px solid var(--color-primary);
  border-radius: var(--radius-sm);
}

.msg__content :deep(code:not(pre code)) {
  padding: 2px 6px;
  font-size: 13px;
  color: var(--color-primary);
  background-color: var(--color-primary-soft);
  border-radius: var(--radius-sm);
}

.msg__content :deep(pre) {
  position: relative;
  margin: 10px 0;
  overflow: hidden;
  background-color: #161b22;
  border-radius: var(--radius-md);
}

.msg__content :deep(pre code) {
  display: block;
  padding: 14px 16px;
  overflow-x: auto;
  font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #e6edf3;
}

.msg__content :deep(.msg-code-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px 6px 14px;
  background-color: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.msg__content :deep(.msg-code-lang) {
  font-size: 12px;
  color: #8b949e;
  text-transform: lowercase;
}

.msg__content :deep(.msg-copy-btn) {
  padding: 2px 8px;
  font-size: 12px;
  color: #8b949e;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
}

.msg__content :deep(.msg-copy-btn:hover) {
  color: #e6edf3;
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
}

.msg__content :deep(table) {
  margin: 10px 0;
  border-collapse: collapse;
}

.msg__content :deep(th),
.msg__content :deep(td) {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
}

.msg__content :deep(th) {
  background-color: var(--bg-tertiary);
}

.msg__content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}

/* ---------- 思考中动画 ---------- */
.msg__thinking {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 18px;
}

.msg__thinking-dot {
  width: 7px;
  height: 7px;
  background-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: msg-dot-bounce 1.2s ease-in-out infinite;
}

.msg__thinking-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.msg__thinking-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes msg-dot-bounce {
  0%,
  60%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-4px);
  }
}

/* ---------- 流式输出光标 ---------- */
.msg__cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  margin-left: 2px;
  vertical-align: -0.15em;
  background-color: var(--color-primary);
  animation: msg-cursor-blink 0.9s steps(2, start) infinite;
}

@keyframes msg-cursor-blink {
  to {
    visibility: hidden;
  }
}
</style>

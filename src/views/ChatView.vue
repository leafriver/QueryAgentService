<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import ChatInput from '@/components/ChatInput.vue'
import MessageItem from '@/components/MessageItem.vue'
import { createConversation, streamChatMessage, type Message } from '@/api/chat'
import { extractErrorMessage } from '@/api/http'

/** 欢迎态示例问题（点击直接发送） */
const suggestions = [
  '帮我生成一段 Python 代码，实现列表去重并保持顺序',
  '如何设计一个高效的数据库索引？',
  '用 Markdown 写一篇产品发布公告',
  '解释一下什么是 RESTful API，并给出示例',
]

const messages = ref<Message[]>([])
const conversationId = ref<number | null>(null)
const streaming = ref(false)
const error = ref('')
const listRef = ref<HTMLElement | null>(null)
const abortController = ref<AbortController | null>(null)

const hasStarted = computed(() => messages.value.length > 0)

/** 判断某条 assistant 消息是否为当前正在流式输出的消息 */
function isStreamingMessage(message: Message): boolean {
  return (
    streaming.value &&
    message.role === 'assistant' &&
    messages.value[messages.value.length - 1] === message
  )
}

/** 滚动到消息列表底部（平滑滚动） */
function scrollToBottom() {
  nextTick(() => {
    const el = listRef.value
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  })
}

/** 生成本地临时消息（id 为负，避免与后端 id 冲突；流结束后用真实 id 校正） */
function createLocalMessage(role: Message['role'], content: string): Message {
  return {
    id: -Date.now() - Math.floor(Math.random() * 1000),
    role,
    content,
    created_at: new Date().toISOString(),
  }
}

async function handleSubmit(text: string) {
  error.value = ''
  if (streaming.value) return

  // 首条消息：先快速建会话（不带 first_message，立即返回会话 id），再统一走流式接口
  if (conversationId.value === null) {
    try {
      const created = await createConversation()
      conversationId.value = created.id
    } catch (err) {
      error.value = extractErrorMessage(err, '创建会话失败，请稍后重试')
      return
    }
  }

  // 立即展示用户消息 + AI 占位消息，随后流式填充
  const userMessage = createLocalMessage('user', text)
  const assistantMessage = createLocalMessage('assistant', '')
  messages.value.push(userMessage, assistantMessage)
  streaming.value = true
  scrollToBottom()

  const controller = new AbortController()
  abortController.value = controller

  // delta 节流：先累积到 pending 缓冲，定时批量 flush，
  // 避免高频更新触发 Markdown 全量重渲染导致卡顿
  let pending = ''
  let flushTimer: ReturnType<typeof setTimeout> | null = null
  const FLUSH_INTERVAL = 60

  const flush = () => {
    if (!pending) return
    assistantMessage.content += pending
    pending = ''
    scrollToBottom()
  }

  try {
    await streamChatMessage(
      conversationId.value,
      { content: text },
      {
        onDelta: (delta) => {
          pending += delta
          if (!flushTimer) {
            flushTimer = setTimeout(() => {
              flushTimer = null
              flush()
            }, FLUSH_INTERVAL)
          }
        },
        onDone: (messageId) => {
          if (flushTimer) {
            clearTimeout(flushTimer)
            flushTimer = null
          }
          flush()
          // 校正为后端真实消息 id（刷新后可正常关联）
          assistantMessage.id = messageId
        },
        onError: (detail) => {
          error.value = detail
        },
      },
      controller.signal,
    )
  } catch (err) {
    // 用户主动点击停止（AbortError）不提示，已生成内容保留在页面
    if (!(err instanceof DOMException && err.name === 'AbortError')) {
      error.value = extractErrorMessage(err, '发送失败，请稍后重试')
    }
  } finally {
    if (flushTimer) {
      clearTimeout(flushTimer)
      flushTimer = null
    }
    flush()
    streaming.value = false
    abortController.value = null
    scrollToBottom()
  }
}

/** 点击停止：中断当前流式生成 */
function handleStop() {
  abortController.value?.abort()
}
</script>

<template>
  <div class="chat-page">
    <!-- 主区域：欢迎态 / 消息流 -->
    <main class="chat-page__main">
      <!-- 欢迎态 -->
      <div v-if="!hasStarted" class="chat-page__welcome">
        <div class="chat-page__hero">
          <h1 class="chat-page__title">有什么可以帮你？</h1>
          <p class="chat-page__subtitle">
            QueryAgent —— 智能体驱动的数据查询服务平台
          </p>
        </div>
        <div class="chat-page__suggestions">
          <button
            v-for="s in suggestions"
            :key="s"
            class="chat-page__suggestion"
            type="button"
            :disabled="streaming"
            @click="handleSubmit(s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <!-- 消息流 -->
      <div v-else ref="listRef" class="chat-page__list">
        <div class="chat-page__column">
          <MessageItem
            v-for="m in messages"
            :key="m.id"
            :message="m"
            :streaming="isStreamingMessage(m)"
          />
        </div>
      </div>
    </main>

    <!-- 底部输入区 -->
    <footer class="chat-page__input">
      <div class="chat-page__column">
        <Transition name="chat-error">
          <p v-if="error" class="chat-page__error">{{ error }}</p>
        </Transition>
        <ChatInput :loading="streaming" @submit="handleSubmit" @stop="handleStop" />
        <p class="chat-page__hint">内容由 AI 生成，请注意甄别</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
  height: calc(100dvh - 56px);
  background:
    radial-gradient(ellipse at top center, var(--color-primary-soft), transparent 60%),
    var(--bg-primary);
  transition: var(--transition-theme);
}

/* ---------- 主区域 ---------- */
.chat-page__main {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

/* 欢迎态 */
.chat-page__welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 24px;
}

.chat-page__hero {
  margin-bottom: 40px;
  text-align: center;
}

.chat-page__title {
  margin: 0 0 10px;
  font-size: 30px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.chat-page__subtitle {
  margin: 0;
  font-size: 15px;
  color: var(--text-muted);
}

.chat-page__suggestions {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 320px));
  gap: 12px;
  justify-content: center;
}

.chat-page__suggestion {
  padding: 14px 18px;
  font-size: 14px;
  text-align: left;
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}

.chat-page__suggestion:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.chat-page__suggestion:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* 消息流 */
.chat-page__list {
  padding: 24px 16px 12px;
}

.chat-page__column {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 860px;
  margin: 0 auto;
}

/* ---------- 底部输入区 ---------- */
.chat-page__input {
  flex-shrink: 0;
  padding: 10px 16px 14px;
  background: linear-gradient(to top, var(--bg-primary) 70%, transparent);
}

.chat-page__error {
  margin: 0 0 8px;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--color-danger);
  background-color: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.25);
  border-radius: var(--radius-md);
}

.chat-page__hint {
  margin: 10px 0 0;
  font-size: 12px;
  text-align: center;
  color: var(--text-muted);
}

/* 错误提示过渡动画 */
.chat-error-enter-active,
.chat-error-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.chat-error-enter-from,
.chat-error-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ---------- 响应式 ---------- */
@media (max-width: 640px) {
  .chat-page__suggestions {
    grid-template-columns: 1fr;
  }

  .chat-page__list {
    padding: 16px 10px 8px;
  }

  .chat-page__title {
    font-size: 24px;
  }
}
</style>

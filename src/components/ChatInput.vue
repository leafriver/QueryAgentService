<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 禁用输入（发送中等场景） */
    disabled?: boolean
    /** 回复中状态：按钮转为加载动画 */
    loading?: boolean
  }>(),
  {
    disabled: false,
    loading: false,
  },
)

const emit = defineEmits<{
  /** 提交消息内容（已去除首尾空白） */
  submit: [text: string]
  /** 停止当前流式生成 */
  stop: []
}>()

const text = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => {
  return text.value.trim().length > 0 && !props.disabled && !props.loading
})

/** 输入区最大高度（px），超出后内部滚动 */
const MAX_HEIGHT = 180

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, MAX_HEIGHT)}px`
}

function handleKeydown(event: KeyboardEvent) {
  // Enter 发送；Shift+Enter 换行；输入法组合状态不触发发送
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    submit()
  }
}

function submit() {
  const content = text.value.trim()
  if (!content || !canSend.value) return
  emit('submit', content)
  text.value = ''
  nextTick(() => {
    autoResize()
    focus()
  })
}

/** 聚焦输入框 */
function focus() {
  textareaRef.value?.focus()
}

defineExpose({ focus })
</script>

<template>
  <div class="chat-input" :class="{ 'is-loading': loading }">
    <textarea
      ref="textareaRef"
      v-model="text"
      class="chat-input__textarea"
      :disabled="disabled || loading"
      rows="1"
      placeholder="给 QueryAgent 发送消息，Enter 发送，Shift+Enter 换行"
      @input="autoResize"
      @keydown="handleKeydown"
    />
    <button
      class="chat-input__send"
      type="button"
      :class="{ 'is-disabled': !canSend && !loading, 'is-stop': loading }"
      :disabled="!canSend && !loading"
      :title="loading ? '停止生成' : '发送消息'"
      @click="loading ? emit('stop') : submit"
    >
      <!-- 生成中：停止方块 -->
      <svg v-if="loading" class="chat-input__icon" viewBox="0 0 24 24" fill="currentColor">
        <rect x="7" y="7" width="10" height="10" rx="1.5" />
      </svg>
      <!-- 常规：纸飞机 -->
      <svg
        v-else
        class="chat-input__icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M22 2 11 13" />
        <path d="M22 2 15 22l-4-9-9-4 20-7z" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 12px 14px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.chat-input:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft), var(--shadow-md);
}

.chat-input__textarea {
  flex: 1;
  min-width: 0;
  max-height: 180px;
  padding: 4px 2px;
  font-family: inherit;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: transparent;
  border: none;
  outline: none;
  resize: none;
}

.chat-input__textarea::placeholder {
  color: var(--text-muted);
}

.chat-input__textarea:disabled {
  cursor: not-allowed;
}

.chat-input__send {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  color: var(--text-inverse);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease, opacity 0.2s ease;
}

.chat-input__send:hover:not(.is-disabled) {
  filter: brightness(1.06);
  box-shadow: 0 4px 12px var(--color-primary-soft);
  transform: translateY(-1px);
}

.chat-input__send:active:not(.is-disabled) {
  transform: translateY(0);
}

.chat-input__send.is-disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

/* 停止生成按钮：红色调，与发送态区分 */
.chat-input__send.is-stop {
  background: linear-gradient(135deg, var(--color-danger), var(--color-danger-hover, var(--color-danger)));
}

.chat-input__icon {
  width: 18px;
  height: 18px;
}

.chat-input__icon--spin {
  animation: chat-input-spin 0.9s linear infinite;
}

@keyframes chat-input-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

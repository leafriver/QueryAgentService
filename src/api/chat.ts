import { getToken } from './http'
import http from './http'

/** 消息角色 */
export type MessageRole = 'user' | 'assistant'

/** 会话列表项 */
export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
}

/** 会话详情（含消息列表） */
export interface ConversationDetail extends Conversation {
  messages: Message[]
}

/** 单条消息 */
export interface Message {
  id: number
  role: MessageRole
  content: string
  created_at: string
}

/** 新建会话请求体 */
export interface CreateConversationPayload {
  title?: string
  first_message?: string
}

/** 发送消息请求体 */
export interface SendMessagePayload {
  content: string
}

/** 发送消息响应：用户消息 + AI 回复 */
export interface MessageExchange {
  user_message: Message
  assistant_message: Message
}

/** 新建会话；携带 first_message 时后端会一并生成模拟 AI 回复 */
export async function createConversation(
  payload: CreateConversationPayload = {},
): Promise<ConversationDetail> {
  const { data } = await http.post<ConversationDetail>('/conversations', payload)
  return data
}

/** 当前用户的会话列表（按更新时间倒序） */
export async function listConversations(): Promise<Conversation[]> {
  const { data } = await http.get<Conversation[]>('/conversations')
  return data
}

/** 会话详情（含消息） */
export async function getConversation(id: number): Promise<ConversationDetail> {
  const { data } = await http.get<ConversationDetail>(`/conversations/${id}`)
  return data
}

/** 删除会话 */
export async function deleteConversation(id: number): Promise<void> {
  await http.delete(`/conversations/${id}`)
}

/** 发送消息：返回用户消息与模拟 AI 回复 */
export async function sendMessage(
  conversationId: number,
  payload: SendMessagePayload,
): Promise<MessageExchange> {
  const { data } = await http.post<MessageExchange>(
    `/conversations/${conversationId}/messages`,
    payload,
  )
  return data
}

/** SSE 事件：文本增量 */
export interface StreamDelta {
  type: 'delta'
  content: string
}

/** SSE 事件：完整回复已落库 */
export interface StreamDone {
  type: 'done'
  message_id: number
}

/** SSE 事件：模型调用错误 */
export interface StreamError {
  type: 'error'
  detail: string
}

/** 后端 SSE 事件联合类型 */
export type StreamChunk = StreamDelta | StreamDone | StreamError

/** 流式响应的回调处理器 */
export interface StreamHandlers {
  /** 收到一段文本增量 */
  onDelta: (content: string) => void
  /** 完整回复已落库 */
  onDone: (messageId: number) => void
  /** 后端返回错误 */
  onError: (detail: string) => void
}

/** 解析一条 SSE 事件文本（形如 "data: {...}"），分发到对应回调 */
function parseSseEvent(event: string, handlers: StreamHandlers): void {
  const dataLine = event
    .split('\n')
    .find((line) => line.startsWith('data:'))
  if (!dataLine) return
  const payload = dataLine.slice(5).trim()
  if (!payload || payload === '[DONE]') return

  try {
    const chunk = JSON.parse(payload) as StreamChunk
    if (chunk.type === 'delta') handlers.onDelta(chunk.content)
    else if (chunk.type === 'done') handlers.onDone(chunk.message_id)
    else if (chunk.type === 'error') handlers.onError(chunk.detail)
  } catch {
    // 忽略无法解析的事件，保证主流程不中断
  }
}

/**
 * 发送消息并流式接收 AI 回复（SSE）。
 *
 * 流式接口不使用 axios（其 15s timeout 不适用于长连接），
 * 改用原生 fetch + ReadableStream 逐块解析，支持通过 signal 中止。
 *
 * 成功返回后表示流已结束（done/error 事件或连接关闭）；
 * 网络异常或非 2xx 响应时抛出 Error（可经 extractErrorMessage 展示）。
 */
export async function streamChatMessage(
  conversationId: number,
  payload: SendMessagePayload,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(
    `/api/v1/conversations/${conversationId}/messages/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken() ?? ''}`,
      },
      body: JSON.stringify(payload),
      signal,
    },
  )

  if (!response.ok || !response.body) {
    const detail = await response.text().catch(() => '')
    throw new Error(detail || `请求失败（${response.status}）`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE 事件以空行（\n\n）分隔，拆出完整事件后解析
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const event of events) {
      parseSseEvent(event, handlers)
    }
  }

  // 处理末尾残留（无空行结尾的最后一个事件）
  const rest = buffer.trim()
  if (rest) parseSseEvent(rest, handlers)
}

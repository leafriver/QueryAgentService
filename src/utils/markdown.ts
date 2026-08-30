import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'

// 代码块使用深色高亮主题（github-dark），与明暗主题下的消息气泡背景均适配
import 'highlight.js/styles/github-dark.css'

/** 初始化 marked：启用代码高亮（langPrefix 对齐 highlight.js 的 CSS 约定） */
marked.use(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    },
  }),
)

/** 解析结果缓存，避免同一文本重复渲染 */
const cache = new Map<string, string>()

/**
 * 将 Markdown 文本渲染为安全 HTML。
 * - 先由 marked 解析为 HTML
 * - 再经 DOMPurify 过滤，防止 XSS
 */
export function renderMarkdown(text: string): string {
  const cached = cache.get(text)
  if (cached !== undefined) return cached

  const raw = marked.parse(text, { async: false }) as string
  const safe = DOMPurify.sanitize(raw)
  cache.set(text, safe)
  return safe
}

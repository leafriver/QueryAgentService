1. 大模型接入层（核心，必做）

选模型：国内直连推荐 DeepSeek / Kimi / 通义千问 / 智谱（OpenAI 兼容协议），或本地 Ollama
config.py 增加配置项：LLM_API_KEY、LLM_BASE_URL、LLM_MODEL，写进 .env，Key 只存后端
后端加依赖：openai（官方 SDK，可直接用 AsyncOpenAI）或 httpx，加入 requirements.txt 并安装


2. 接口改造（必做）

把 chat.py 两处 _build_mock_reply 换成真实调用
上下文：调模型时要带上该会话的历史消息列表（user/assistant 交替），否则模型"失忆"
流式响应：LLM 生成要数秒到数十秒，同步请求会卡死页面。需把接口改成 SSE 流式输出，前端逐字显示——这是"像 ChatGPT"的关键


3. 前端流式适配（必做）

api/chat.ts 已预留但需真正实现：fetch + ReadableStream 逐段读取、解析 SSE 数据块
ChatView.vue 增加：AI 消息占位 + 逐字追加、"停止生成"按钮、生成中禁用输入


4. 健壮性处理（必做）

LLM 超时、调用失败时的兜底文案（不要整个请求挂掉）
上下文长度控制（历史消息太多时截断，防止超 token 上限）
system prompt 设计（如"你是 QueryAgent 智能助手…"）


5. 可选增强（后期）

界面选择模型 / 显示思考过程（reasoning 模型） / 会话标题自动生成
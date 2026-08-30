# Server（后端）

基于 Python + FastAPI 的后端服务。

## 目录结构

```
server/
├── app/
│   ├── main.py               # 应用入口
│   ├── core/
│   │   └── config.py         # 全局配置（支持 .env）
│   └── api/
│       ├── router.py         # 路由汇总
│       └── endpoints/        # 具体接口
├── requirements.txt
├── .env.example
└── README.md
```

## 快速开始

```bash
cd server

# 1. 创建虚拟环境（可选，推荐）
python -m venv .venv

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（可选）
# Windows: copy .env.example .env
# macOS/Linux: cp .env.example .env

# 4. 启动开发服务（默认 http://127.0.0.1:8000）
uvicorn app.main:app --reload
```

## 接口文档

启动后访问：

- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

## 约定

- 所有业务接口统一挂载在 `/api/v1` 前缀下。
- 新增接口时，在 `app/api/endpoints/` 下新建模块，并在 `app/api/router.py` 中注册。

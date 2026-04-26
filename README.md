# ChatBI 股票投资助手

基于 LangChain + LangGraph + Vue 3 的智能股票分析助手，支持股价查询、趋势预测、异常检测等功能。

## 📋 项目结构

```
CASE-ChatBI投资助手/
├── backend/                    # 后端 (FastAPI + LangChain)
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── api/               # API 路由
│   │   ├── core/              # Agent 和工具
│   │   └── utils/             # 工具函数
│   └── requirements.txt       # Python 依赖
│
├── stock-vue-frontend/         # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── App.vue            # 主组件
│   │   └── main.js            # 入口文件
│   ├── public/                # 静态资源
│   └── package.json
│
├── image_show/                 # 图片存储目录
├── gold_data.db                # SQLite 数据库
├── stock_history_data.xlsx     # 数据备份
├── init_db.py                  # 数据库初始化脚本
└── faq.txt                     # FAQ 配置
```

## 🚀 快速开始

### 1. 环境准备

- Python 3.10+
- Node.js 18+
- OpenRouter API Key

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（Windows）
set OPENROUTER_API_KEY=your_api_key

# 启动服务
python -m app.main
```

后端服务运行在 `http://localhost:8000`

### 3. 前端启动

```bash
# 进入前端目录
cd stock-vue-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在 `http://localhost:5173`

### 4. 数据库初始化（可选）

如果数据库文件丢失，可以从 Excel 恢复：

```bash
python init_db.py
```

## ✨ 功能特性

- 📊 **股价查询**: 查询历史股价数据
- 📈 **趋势预测**: ARIMA/Prophet 算法预测
- 🔍 **异常检测**: 布林带超买超卖分析
- 🌐 **联网搜索**: Tavily MCP 在线搜索
- 💬 **流式输出**: 实时打字机效果
- 🖼️ **图片预览**: 点击全屏查看图表

## 🛠️ 技术栈

**后端:**
- FastAPI + Uvicorn
- LangChain + LangGraph
- OpenRouter (tencent/hy3-preview:free)
- SQLite + Pandas
- Matplotlib (图表生成)

**前端:**
- Vue 3 (Composition API)
- Vite
- Element Plus
- Fetch API (SSE)

## 📝 环境变量

创建 `.env` 文件（或使用系统环境变量）：

```bash
OPENROUTER_API_KEY=your_api_key_here
MODEL_NAME=tencent/hy3-preview:free
MODEL_SERVER=https://openrouter.ai/api/v1
```

## ⚠️ 注意事项

1. 数据库文件 `gold_data.db` 包含在项目中，但图片目录 `image_show/` 需要手动创建
2. 所有生成的图片会保存在 `image_show/` 目录
3. 首次运行需要初始化数据库（已有 `gold_data.db` 可跳过）

## 📄 许可证

MIT License

# 智净通 - 智能清洁机器人AI客服系统

基于RAG（Retrieval-Augmented Generation）技术的智能客服系统，结合FastAPI后端和Streamlit前端，提供智能问答、个性化报告生成等功能。系统支持智能清洁机器人的产品咨询、使用指导、故障排查等场景的智能问答服务。

## 技术栈

- **后端框架**: FastAPI >= 0.115.0
- **前端框架**: Streamlit >= 1.32.0
- **数据库**: SQLite + SQLAlchemy >= 2.0
- **向量数据库**: ChromaDB
- **LLM框架**: LangChain + 通义千问
- **认证**: JWT + OAuth2

## 项目结构

```
├── app.py                    # Streamlit前端入口
├── run_backend.py            # FastAPI后端启动脚本
├── requirements.txt          # 项目依赖
├── .env                      # 环境变量配置
├── backend/                  # FastAPI后端模块
│   ├── main.py              # 应用入口
│   ├── database.py          # 数据库配置
│   ├── models.py            # SQLAlchemy模型
│   ├── schemas.py           # Pydantic数据模型
│   ├── dependencies.py      # 依赖注入（认证等）
│   └── routes/              # API路由
│       ├── users.py         # 用户管理API
│       ├── chat.py          # 智能对话API
│       ├── documents.py     # 文档管理API
│       └── reports.py       # 报告生成API
├── agent/                    # 智能体模块
│   ├── react_agent.py       # ReAct智能体
│   └── tools/               # 工具函数
├── rag/                     # RAG模块
│   ├── rag_service.py       # RAG服务
│   └── vector_store.py      # 向量存储服务
├── model/                   # 模型工厂
│   └── factory.py           # LLM和Embedding模型
├── utils/                   # 工具函数
│   ├── config_handler.py    # 配置管理
│   ├── prompt_loader.py     # 提示词加载
│   ├── file_handler.py      # 文件处理
│   ├── path_tool.py         # 路径工具
│   └── logger_handler.py    # 日志处理
├── config/                  # 配置文件
│   ├── rag.yml              # RAG配置
│   ├── chroma.yml           # Chroma配置
│   ├── prompts.yml          # 提示词配置
│   └── agent.yml            # 智能体配置
└── data/                    # 知识库数据
```

## 核心功能

### 1. 智能问答系统
- 基于RAG技术的精准问答服务
- 融合向量检索与LLM生成能力
- 支持产品咨询、使用指导、故障排查等场景
- 流式响应，提升用户体验

### 2. 用户管理系统
- JWT Token用户认证
- 安全的密码加密存储（bcrypt）
- OAuth2标准授权流程

### 3. 文档知识库
- 支持PDF/TXT文档上传
- 向量化存储与语义检索
- 文档MD5去重机制

### 4. 个性化报告生成
- 基于用户历史数据的智能分析
- 设备使用情况报告
- 维护保养建议

## 快速开始

### 环境要求
- Python 3.10+
- pip 20.0+

### 安装依赖

```bash
pip install -r requirements.txt
pip install pydantic[email] dashscope "numpy<2.0"
```

### 启动后端服务

```bash
python run_backend.py
```

后端服务将在 `http://localhost:8000` 启动

### 启动前端应用

```bash
streamlit run app.py
```

前端应用将在 `http://localhost:8501` 启动

## API文档

启动后端服务后，可访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API端点

| 模块 | 方法 | 端点 | 描述 |
|------|------|------|------|
| 用户管理 | POST | `/api/users/register` | 用户注册 |
| 用户管理 | POST | `/api/users/login` | 用户登录 |
| 用户管理 | GET | `/api/users/me` | 获取当前用户 |
| 智能对话 | POST | `/api/chat/` | 发起对话 |
| 智能对话 | POST | `/api/chat/stream` | 流式对话 |
| 智能对话 | GET | `/api/chat/history` | 获取对话历史 |
| 文档管理 | GET | `/api/documents/` | 获取文档列表 |
| 文档管理 | POST | `/api/documents/upload` | 上传文档 |
| 文档管理 | DELETE | `/api/documents/{id}` | 删除文档 |
| 报告生成 | POST | `/api/reports/` | 生成报告 |
| 报告生成 | GET | `/api/reports/` | 获取报告列表 |

## 系统架构

```
用户请求 → FastAPI后端 → ReAct智能体
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         RAG检索     外部数据API    天气/用户API
              ↓            ↓            ↓
              └────────────┼────────────┘
                           ↓
                      LLM生成回复
                           ↓
                      流式响应用户
```

## 项目亮点

1. **RAG技术落地**: 融合向量检索与LLM生成，实现精准的语义理解与问答
2. **ReAct智能体**: 实现"思考-行动-观察-再思考"的推理链路
3. **模块化架构**: 清晰的代码结构，支持快速迭代开发
4. **RESTful API**: 标准化的接口设计，实现前后端完全解耦
5. **流式响应**: SSE实时推送，提升用户交互体验
6. **知识库管理**: 自动化文档处理，支持PDF/TXT解析与向量化
7. **JWT安全认证**: Token认证机制，保障用户数据安全
8. **单元测试**: pytest测试框架，覆盖核心API和业务逻辑
9. **异常处理**: 统一的异常处理机制，规范的错误响应格式
10. **缓存优化**: 内存缓存机制，优化重复查询性能

## 单元测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov httpx

# 运行所有测试
python run_tests.py

# 或直接使用pytest
pytest tests/ -v
```

### 测试覆盖

| 测试模块 | 测试内容 |
|----------|----------|
| 健康检查 | 根路径、健康检查API |
| 用户管理 | 注册、登录、重复检测 |
| 密码安全 | 加密、验证 |
| JWT Token | 令牌生成、过期处理 |
| 数据模型 | Pydantic验证 |
| 认证保护 | 无Token访问、无效Token |

# 智净通项目 - 3天面试速成指南

> **目标**: 3天内完全掌握项目，经得起面试官任何追问  
> **剩余时间**: 16天放暑假（时间充裕）

---

## 📅 学习计划

### 紧急版（3天）

| 天数 | 任务 | 目标 |
|------|------|------|
| 第1天 | 理解架构 + RAG核心 | 能画架构图、解释RAG原理 |
| 第2天 | 吃透ReAct + 代码细节 | 能手写核心代码、解释原理 |
| 第3天 | 背面试题 + 模拟提问 | 能流畅回答任何问题 |

### 超详细版（如果3天不够）

| 天数 | 上午(3h) | 下午(3h) | 晚上(2h) |
|------|----------|----------|----------|
| Day1 | 项目架构 | RAG原理 | 画架构图 |
| Day2 | ReAct原理 | 代码走读 | 工具函数 |
| Day3 | FastAPI | 数据库设计 | 面试题 |
| Day4 | LangChain | 中间件 | 深入细节 |
| Day5 | 缓存机制 | 异常处理 | 总结复习 |
| Day6 | 完整过一遍 | 模拟面试 | 查漏补缺 |
| Day7 | 轻量复习 | 准备问题 | 放松休息 |

---

## 📖 第一部分：项目整体理解（必须掌握）

### 1.1 一句话描述项目

```
智净通是一个基于RAG技术的智能客服系统，
为智能清洁机器人产品提供7×24h智能问答服务。
```

### 1.2 核心架构（必须能画出来）

```
┌─────────────────────────────────────────────────────┐
│                     用户请求                          │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI 后端 (端口8000)                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │用户管理  │  │智能对话  │  │文档管理  │  │报告生成  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘ │
└───────┼────────────┼────────────┼────────────┼───────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────┐
│                   ReAct 智能体                       │
│         (思考→行动→观察→再思考 循环)                  │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ RAG检索  │  │天气查询  │  │用户数据  │  │外部数据  │
│ (向量库) │  │          │  │          │  │          │
└────┬─────┘  └──────────┘  └──────────┘  └──────────┘
     │
     ▼
┌──────────┐
│ LLM生成  │  ← 通义千问
└────┬─────┘
     │
     ▼
┌──────────┐
│ SSE流式响应
└──────────┘
```

**面试时能说出来**：用户请求进入FastAPI后，由ReAct智能体处理。智能体根据问题选择调用不同工具（检索知识库、查天气、查用户数据），最后由LLM生成回答，通过SSE流式推送给用户。

### 1.3 技术栈（必须记住）

| 层级 | 技术 | 作用 |
|------|------|------|
| 后端框架 | FastAPI | 高性能API服务 |
| 数据库 | SQLite + SQLAlchemy | 用户数据存储 |
| 向量数据库 | ChromaDB | 文档向量存储 |
| AI框架 | LangChain | Agent编排 |
| LLM | 通义千问(Qwen) | 生成回答 |
| 前端 | Streamlit | 可视化界面 |
| 认证 | JWT | 用户身份验证 |

---

## 📖 第二部分：核心技术原理（面试必问）

### 2.1 RAG技术原理 ⭐⭐⭐⭐⭐

#### 什么是RAG？

```
RAG = Retrieval Augmented Generation（检索增强生成）

原理：
1. 用户提问
2. 将问题转为向量
3. 在向量数据库中检索相似内容
4. 将检索结果+问题一起发给LLM
5. LLM生成最终回答
```

#### 为什么用RAG？（面试必问）

```
不用RAG的问题：
- LLM知识可能过时
- LLM可能胡编乱造（幻觉）
- 无法回答垂直领域专业问题

用RAG的好处：
- 答案基于真实知识库，不会胡说
- 可以回答最新/专业问题
- 答案可溯源
```

#### 项目中RAG的实现

```python
# rag_service.py
class RagSummarizeService:
    def rag_summarize(self, query):
        # 1. 从向量库检索相关内容
        context_docs = self.retriever.invoke(query)
        
        # 2. 组装上下文
        context = ""
        for doc in context_docs:
            context += f"【参考资料】: {doc.page_content}\n"
        
        # 3. 发给LLM生成
        return self.chain.invoke({
            "input": query,
            "context": context
        })
```

**能说出来**：当用户问问题时，先在ChromaDB中检索相关的知识库内容，然后把这些内容和问题一起发给通义千问，让它基于真实资料生成回答。

---

### 2.2 ReAct智能体原理 ⭐⭐⭐⭐⭐

#### 什么是ReAct？

```
ReAct = Reasoning + Acting（推理 + 行动）

核心思想：
- 不是直接回答，而是先"思考"再"行动"
- 行动后观察结果，继续思考
- 循环直到足够回答问题
```

#### 执行流程（必须能画出来）

```
用户问题 → Thought(思考) → Action(行动) → Observation(观察)
    ↑                                              │
    └───────────────── 再思考 ←────────────────────┘
                                                    ↓
                                              足够 → Final Answer
```

#### 项目中ReAct的实现

```python
# agent_tools.py - 定义工具
@tool(description="从向量库检索资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取城市天气")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，26度"

# react_agent.py - 创建Agent
class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,          # 通义千问
            system_prompt=系统提示词,
            tools=[                   # 7个工具
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                get_current_month,
                fetch_external_data,
                fill_context_for_report
            ],
            middleware=[监控中间件, 日志中间件, 提示词切换中间件]
        )
```

**能说出来**：智能体拿到用户问题后，会"思考"需要调用哪个工具。比如用户问"深圳适合用扫地机器人吗"，它会先思考需要知道深圳的天气，然后调用get_weather工具获取天气信息，再综合给出建议。

---

### 2.3 FastAPI核心特性 ⭐⭐⭐⭐

#### 为什么用FastAPI？

```
1. 高性能 - 异步处理，并发能力强
2. 自动文档 - Swagger UI / ReDoc
3. 类型安全 - Pydantic数据验证
4. 依赖注入 - 统一管理认证、数据库等
```

#### 项目中的API设计

```python
# 路由注册
app.include_router(users, prefix="/api/users")
app.include_router(chat, prefix="/api/chat")

# API端点示例
@router.post("/register")  # 注册用户
@router.post("/login")     # 登录
@router.post("/chat/")      # 对话
@router.get("/history")     # 历史记录
```

#### 请求流程

```
请求 → 中间件 → 依赖注入(认证) → 路由处理 → 业务逻辑 → 响应
```

---

### 2.4 JWT认证原理 ⭐⭐⭐⭐

#### 什么是JWT？

```
JWT = JSON Web Token（JSON格式的令牌）

结构：
┌─────────────┬─────────────┬─────────────┐
│ Header      │ Payload    │ Signature   │
│ (算法信息)   │ (用户数据)  │ (防伪造)    │
└─────────────┴─────────────┴─────────────┘
```

#### 项目中的JWT流程

```python
# 1. 登录时生成Token
def login(user):
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# 2. 请求时验证Token
@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user
```

**能说出来**：用户登录后，服务端用密钥生成一个JWT令牌返回给客户端。之后客户端每次请求带上这个令牌，服务端验证令牌中的用户信息来识别身份。

---

## 📖 第三部分：面试高频问题及标准回答

### Q1: 请介绍一下你这个项目

**参考回答（1分钟版）**：
```
这是一个基于RAG技术的智能客服系统，叫智净通。

用户可以像跟人聊天一样问问题，系统会结合知识库检索
和LLM生成，给出专业、准确的回答。

技术栈：FastAPI做后端，LangChain做AI编排，
ChromaDB存向量，SQLite存用户数据。

核心亮点是实现了ReAct智能体，能自主选择调用
天气查询、用户数据检索等多种工具来回答问题。
```

### Q2: 什么是RAG？为什么用RAG？

**参考回答**：
```
RAG是Retrieval Augmented Generation，检索增强生成。

简单说就是：用户提问 → 检索相关资料 → LLM基于资料生成回答

为什么用RAG：
1. 避免LLM胡说八道 - 答案基于真实知识库
2. 支持垂直领域 - 可以用我们自己的产品文档
3. 知识可更新 - 改知识库就行，不用重新训练模型
```

### Q3: 什么是ReAct？你怎么实现的？

**参考回答**：
```
ReAct是Reasoning + Acting，推理+行动。

核心思想是让AI不是直接回答，而是先思考、调用工具、观察结果，
再思考...循环直到能回答问题。

我的实现：
1. 用LangChain的create_agent创建Agent
2. 定义了7个工具函数（查天气、查用户、检索知识库等）
3. 通过中间件监控工具调用、动态切换提示词

比如用户问"深圳适合用扫地机吗"，
Agent会先思考"需要知道深圳天气"，然后调用天气工具，
再综合给出建议。
```

### Q4: FastAPI相比Django/Flask有什么优势？

**参考回答**：
```
1. 性能 - 异步非阻塞，并发处理能力强
2. 自动文档 - 写完API就有Swagger UI，不用手动写文档
3. 类型安全 - Pydantic自动验证请求参数
4. 依赖注入 - 认证、数据库等可以统一管理

实际项目体验：写API特别快，参数自动验证，出错直接返回规范错误。
```

### Q5: ChromaDB是什么？和传统数据库有什么区别？

**参考回答**：
```
ChromaDB是向量数据库，专门存储和检索向量。

区别：
- 传统数据库：存储精确数据，查询"等于什么"
- 向量数据库：存储语义向量，查询"相似什么"

比如：
- 传统数据库查"扫地机器人"，只能找到标题含这个词的
- 向量数据库查"扫地机器人"，能理解语义，找到吸尘器、自动清洁等相关文章

原理：将文本转为向量（数字列表），通过余弦相似度找最相似的。
```

### Q6: 你遇到的最大技术难点是什么？

**参考回答（可选）**：
```
我遇到的一个难点是：怎么让Agent在报告生成场景下
自动切换提示词。

解决思路：
1. 用中间件拦截工具调用
2. 当调用fill_context_for_report时，设置标记
3. 在生成回答前，检查这个标记，动态切换系统提示词

这样同一个Agent，可以处理普通问答和报告生成两种场景。
```

### Q7: 你们的向量检索是怎么优化的？

**参考回答（可选）**：
```
1. 文档分块策略 - 根据语义分段，不是简单按字数切
2. 元数据管理 - 每个向量带来源文档信息，方便追溯
3. MD5去重 - 避免重复文档入库

如果深入问：可以说重排序、混合检索等（但项目没做的话别说）
```

### Q8: SSE流式响应是什么？

**参考回答**：
```
SSE = Server-Sent Events，服务器推送事件。

传统的HTTP请求：客户端发请求 → 服务端返回完整响应
SSE：服务端边生成边推送，客户端像打字一样看到内容

好处：用户体验好，感觉是"实时"在回答
实现：Flask的stream_with_context，或者FastAPI的StreamingResponse
```

---

## 📖 第四部分：必须掌握的代码片段

### 4.1 工具定义（能说出来）

```python
@tool(description="获取城市天气")
def get_weather(city: str) -> str:
    return f"{city}天气晴朗，26度"

# 关键点：
# 1. @tool装饰器标记
# 2. 有清晰的description（Agent靠这个理解何时调用）
# 3. 类型注解
```

### 4.2 Agent创建（能说出来）

```python
agent = create_agent(
    model=chat_model,        # 通义千问
    system_prompt=提示词,
    tools=[工具列表],
    middleware=[中间件列表]
)

# 关键点：
# 1. model是LLM
# 2. tools是Agent能调用的函数
# 3. middleware可以做监控、动态提示词等
```

### 4.3 RAG检索（能说出来）

```python
# 1. 检索
docs = vectorstore.as_retriever().invoke("用户问题")

# 2. 组装上下文
context = "\n".join([doc.page_content for doc in docs])

# 3. 发给LLM
response = chain.invoke({"input": query, "context": context})
```

### 4.4 JWT认证（能说出来）

```python
# 生成Token
token = create_access_token({"sub": user.username})

# 验证Token
@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user
```

---

## 📖 第五部分：面试加分项

### 5.1 可以提的优化点

```
1. 重排序：对初步检索结果再排序，提高相关性
2. 混合检索：结合关键词+向量检索
3. 缓存：对高频问题缓存结果
4. 限流：防止恶意请求
```

### 5.2 可以提的后续规划

```
1. 支持更多文档格式（Word、Excel）
2. 多轮对话记忆
3. A/B测试不同提示词效果
4. 用户反馈闭环
```

### 5.3 面试时可以反问的问题

```
1. 团队的技术栈是怎样的？
2. 这个岗位主要做什么方向？
3. 入职后有mentor带吗？
4. 技术分享的氛围怎么样？
```

---

## 📖 第六部分：快速自测清单

### 必须能回答"是"的检查项

- [ ] 能画出完整的项目架构图
- [ ] 能解释什么是RAG（检索增强生成）
- [ ] 能解释什么是ReAct（推理+行动）
- [ ] 能说出项目的技术栈
- [ ] 能解释JWT认证流程
- [ ] 能说出RAG的工作流程
- [ ] 能解释FastAPI的优势
- [ ] 能解释向量数据库的作用
- [ ] 能说出Agent调用的主要工具
- [ ] 能回答"你遇到的最大难点是什么"

### 如果都能回答"是"，面试稳了！

---

## 📝 附录：常用术语表

| 术语 | 解释 |
|------|------|
| RAG | Retrieval Augmented Generation，检索增强生成 |
| ReAct | Reasoning + Acting，推理+行动 |
| LLM | Large Language Model，大语言模型 |
| SSE | Server-Sent Events，服务器推送事件 |
| JWT | JSON Web Token，身份令牌 |
| 向量 | 文本的数学表示（数字列表） |
| Embedding | 将文本转为向量的过程 |
| Agent | 能够自主决策和执行任务的AI系统 |
| Middleware | 中间件，拦截和处理请求/响应的组件 |

---

## 🎯 最后提醒

1. **不要背答案** - 理解原理，用自己的话表达
2. **不懂就说不懂** - "这个我没深入了解，但我的理解是..."
3. **展示思考过程** - 面试官更看重你怎么想
4. **项目放GitHub** - 有链接加分，面试官可能去看

**祝你面试顺利！🎉**

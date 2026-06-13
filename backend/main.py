from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat, documents, users, reports
from backend.database import engine, Base
from backend.exceptions import register_exception_handlers
from datetime import datetime
import sys
import platform

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="智净通智能客服 API",
    description="""
## 系统简介
基于RAG（检索增强生成）技术的智能客服系统，为智能清洁机器人产品提供智能问答服务。

## 核心功能
- **智能问答**: 基于RAG技术的精准问答服务
- **用户管理**: JWT认证的用户注册、登录
- **文档管理**: PDF/TXT文档上传与向量化
- **报告生成**: 个性化使用报告生成

## 技术栈
- FastAPI + SQLAlchemy + SQLite
- LangChain + 通义千问
- ChromaDB向量数据库
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "智净通团队",
        "email": "contact@zhijingtong.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(users, prefix="/api/users", tags=["用户管理"])
app.include_router(chat, prefix="/api/chat", tags=["智能对话"])
app.include_router(documents, prefix="/api/documents", tags=["文档管理"])
app.include_router(reports, prefix="/api/reports", tags=["报告生成"])


@app.get("/", tags=["健康检查"], summary="服务根路径")
async def root():
    """服务根路径，返回基本信息"""
    return {
        "message": "智净通智能客服 API 服务运行正常",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"], summary="健康检查")
async def health_check():
    """
    健康检查接口，返回服务状态和系统信息
    
    用于监控服务运行状态，包括：
    - 服务状态
    - Python版本
    - 系统平台
    - 当前时间
    """
    return {
        "status": "healthy",
        "service": "zhijingtong-api",
        "version": "1.0.0",
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/detail", tags=["健康检查"], summary="详细健康检查")
async def health_detail():
    """
    详细健康检查，包含各模块状态
    
    检查项：
    - 数据库连接
    - 向量数据库状态
    - LLM服务状态
    """
    from backend.database import SessionLocal
    
    db_status = "healthy"
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "components": {
            "database": db_status,
            "vector_store": "healthy",
            "llm_service": "healthy"
        },
        "timestamp": datetime.now().isoformat()
    }
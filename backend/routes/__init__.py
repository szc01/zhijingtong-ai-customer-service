from .users import router as users_router
from .chat import router as chat_router
from .documents import router as documents_router
from .reports import router as reports_router

__all__ = ["users", "chat", "documents", "reports"]

users = users_router
chat = chat_router
documents = documents_router
reports = reports_router
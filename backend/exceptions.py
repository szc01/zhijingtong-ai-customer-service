"""
智净通智能客服系统 - 异常处理模块
提供统一的异常处理和错误响应格式
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用自定义异常基类"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


class ResourceNotFoundException(AppException):
    """资源不存在异常"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} '{identifier}' 不存在",
            status_code=status.HTTP_404_NOT_FOUND
        )


class AuthenticationException(AppException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PermissionDeniedException(AppException):
    """权限拒绝异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            code="PERMISSION_DENIED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class DatabaseException(AppException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceException(AppException):
    """外部服务异常"""
    def __init__(self, service: str, message: str):
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service} 服务异常: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict = None
) -> JSONResponse:
    """创建统一的错误响应"""
    content = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }
    if details:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)


async def app_exception_handler(request: Request, exc: AppException):
    """自定义异常处理器"""
    logger.warning(f"AppException: {exc.code} - {exc.message}")
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error.get("loc", []),
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    logger.warning(f"Validation error: {errors}")
    return create_error_response(
        code="VALIDATION_ERROR",
        message="请求参数验证失败",
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"errors": errors}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return create_error_response(
        code="DATABASE_ERROR",
        message="数据库操作失败，请稍后重试",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    logger.debug(traceback.format_exc())
    return create_error_response(
        code="INTERNAL_ERROR",
        message="服务器内部错误，请稍后重试",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
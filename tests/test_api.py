"""
智净通智能客服系统 - 单元测试
测试覆盖：用户管理、API健康检查、数据模型验证
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend import models, schemas
from backend.dependencies import get_password_hash, verify_password, create_access_token


# 测试数据库配置（使用内存数据库）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 测试数据库依赖
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db


# 测试客户端
client = TestClient(app)


# ==================== 数据库初始化 ====================
@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前创建表，测试后删除"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==================== 健康检查测试 ====================
class TestHealthCheck:
    """健康检查API测试"""

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_endpoint(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ==================== 用户管理测试 ====================
class TestUserManagement:
    """用户管理API测试"""

    def test_user_registration_success(self):
        """测试用户注册成功"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/api/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_user_registration_duplicate_username(self):
        """测试重复用户名注册"""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpassword123"
        }
        client.post("/api/users/register", json=user_data)
        
        # 再次注册相同用户名
        user_data2 = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/users/register", json=user_data2)
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]

    def test_user_registration_duplicate_email(self):
        """测试重复邮箱注册"""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/users/register", json=user_data)
        
        # 再次注册相同邮箱
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/users/register", json=user_data2)
        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]

    def test_user_login_success(self):
        """测试用户登录成功"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/users/register", json=user_data)
        
        # 登录
        response = client.post(
            "/api/users/login",
            data={"username": "testuser", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_wrong_password(self):
        """测试密码错误登录"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/users/register", json=user_data)
        
        response = client.post(
            "/api/users/login",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_get_current_user(self):
        """测试获取当前用户信息"""
        # 注册并登录
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/api/users/register", json=user_data)
        
        login_response = client.post(
            "/api/users/login",
            data={"username": "testuser", "password": "testpassword123"}
        )
        token = login_response.json()["access_token"]
        
        # 获取用户信息
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"


# ==================== 密码安全测试 ====================
class TestPasswordSecurity:
    """密码加密与验证测试"""

    def test_password_hashing(self):
        """测试密码加密"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_password_verification_correct(self):
        """测试密码验证正确"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_password_verification_wrong(self):
        """测试密码验证错误"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False


# ==================== JWT Token测试 ====================
class TestJWTToken:
    """JWT Token测试"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        assert token is not None
        assert len(token) > 50

    def test_token_with_expiry(self):
        """测试带过期时间的令牌"""
        from datetime import timedelta
        data = {"sub": "testuser"}
        token = create_access_token(data, timedelta(minutes=30))
        assert token is not None


# ==================== 数据模型测试 ====================
class TestSchemas:
    """Pydantic数据模型测试"""

    def test_user_create_valid(self):
        """测试有效的用户创建数据"""
        user = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_create_invalid_email(self):
        """测试无效邮箱"""
        with pytest.raises(ValueError):
            schemas.UserCreate(
                username="testuser",
                email="invalid-email",
                password="testpassword123"
            )

    def test_chat_request_valid(self):
        """测试有效的聊天请求"""
        request = schemas.ChatRequest(message="你好")
        assert request.message == "你好"

    def test_report_request_valid(self):
        """测试有效的报告请求"""
        request = schemas.ReportRequest(user_id=1, report_type="monthly")
        assert request.user_id == 1
        assert request.report_type == "monthly"


# ==================== 认证保护测试 ====================
class TestAuthenticationProtection:
    """认证保护测试"""

    def test_protected_endpoint_without_token(self):
        """测试无Token访问保护端点"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self):
        """测试无效Token访问"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_chat_endpoint_requires_auth(self):
        """测试聊天端点需要认证"""
        response = client.post(
            "/api/chat/",
            json={"message": "你好"}
        )
        assert response.status_code == 401


# ==================== 运行测试 ====================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
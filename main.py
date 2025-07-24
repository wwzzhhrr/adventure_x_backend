import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.auth import router as auth_router
from app.database import engine
from app.models.user import Base

# 加载环境变量
load_dotenv()

# 应用配置
APP_TITLE = os.getenv("APP_TITLE", "AdventureX Backend")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "AdventureX Backend API")


def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例"""
    app = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源，生产环境应该指定具体域名
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有请求头
    )
    
    # 注册路由
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    
    return app


def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


# 创建应用实例
app = create_app()

# 初始化数据库
init_database()


@app.get("/", tags=["health"])
def read_root():
    """健康检查端点"""
    return {
        "message": APP_DESCRIPTION,
        "version": APP_VERSION,
        "status": "healthy"
    }


@app.get("/hello/{name}", tags=["demo"])
async def say_hello(name: str):
    """示例问候端点"""
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    import uvicorn
    
    # 服务器配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
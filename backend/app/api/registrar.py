#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from backend.app.api.routers import v1
from backend.app.common.exception.exception_handler import register_exception
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.database.db_mysql import create_table
from backend.app.middleware import register_middleware


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
        openapi_url=settings.OPENAPI_URL
    )

    if settings.STATIC_FILES:
        # 注册静态文件
        register_static_file(app)

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

    # 初始化连接
    register_init(app)

    # 分页
    register_page(app)

    # 全局异常处理
    register_exception(app)

    return app


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """
    app.include_router(
        v1,
    )


def register_static_file(app: FastAPI):
    """
    静态文件交互开发模式, 生产使用 nginx 静态资源服务

    :param app:
    :return:
    """
    import os
    from fastapi.staticfiles import StaticFiles
    if not os.path.exists("./static"):
        os.mkdir("./static")
    app.mount("/static", StaticFiles(directory="static"), name="static")


def register_init(app: FastAPI):
    """
    初始化连接

    :param app: FastAPI
    :return:
    """

    @app.on_event("startup")
    async def startup_event():
        # 创建数据库表
        await create_table()
        if settings.REDIS_OPEN:
            # 连接redis
            await redis_client.init_redis_connect()

    @app.on_event("shutdown")
    async def shutdown_event():
        if settings.REDIS_OPEN:
            # 关闭redis连接
            await redis_client.close()


def register_page(app: FastAPI):
    """
    分页查询

    :param app:
    :return:
    """
    add_pagination(app)

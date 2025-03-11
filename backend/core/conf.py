#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.path_conf import BasePath


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    # Env Config
    ENVIRONMENT: Literal['dev', 'pro']

    # Env Database
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    # Env Token
    TOKEN_SECRET_KEY: str  # 密钥 secrets.token_urlsafe(32)

    # FastAPI
    FASTAPI_API_V1_PATH: str = '/api/v1'
    FASTAPI_TITLE: str = 'FastAPI'
    FASTAPI_VERSION: str = '0.0.1'
    FASTAPI_DESCRIPTION: str = 'FastAPI Best Architecture'
    FASTAPI_DOCS_URL: str = '/docs'
    FASTAPI_REDOC_URL: str = '/redoc'
    FASTAPI_OPENAPI_URL: str | None = '/openapi'
    FASTAPI_STATIC_FILES: bool = False

    @model_validator(mode='before')
    @classmethod
    def validator_api_url(cls, values):
        if values['ENVIRONMENT'] == 'pro':
            values['FASTAPI_OPENAPI_URL'] = None
            values['FASTAPI_STATIC_FILES'] = False
        return values

    # MYSQL
    DATABASE_ECHO: bool = False
    DATABASE_POOL_ECHO: bool = False
    DATABASE_SCHEMA: str = 'fsm'
    DATABASE_CHARSET: str = 'utf8mb4'

    # Redis
    REDIS_TIMEOUT: int = 10

    # Captcha
    CAPTCHA_LOGIN_REDIS_PREFIX: str = 'fba:login:captcha'
    CAPTCHA_LOGIN_EXPIRE_SECONDS: int = 60 * 5  # 过期时间，单位：秒

    # Token
    TOKEN_ALGORITHM: str = 'HS256'  # 算法
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # 过期时间，单位：秒
    TOKEN_URL_SWAGGER: str = f'{FASTAPI_API_V1_PATH}/auth/login/swagger'

    # Log
    LOG_STD_LEVEL: str = 'INFO'
    LOG_ACCESS_FILE_LEVEL: str = 'INFO'
    LOG_ERROR_FILE_LEVEL: str = 'ERROR'
    LOG_STD_FORMAT: str = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | <lvl>{message}</>'
    LOG_FILE_FORMAT: str = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | <lvl>{message}</>'
    LOG_ACCESS_FILENAME: str = 'fba_access.log'
    LOG_ERROR_FILENAME: str = 'fba_error.log'

    # 中间件
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://127.0.0.1:8000',
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        '*',
    ]

    # DateTime
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Request limiter
    REQUEST_LIMITER_REDIS_PREFIX: str = 'fba:limiter'

    # Demo mode (Only GET, OPTIONS requests are allowed)
    DEMO_MODE: bool = False
    DEMO_MODE_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/login'),
        ('POST', f'{FASTAPI_API_V1_PATH}/auth/logout'),
        ('GET', f'{FASTAPI_API_V1_PATH}/auth/captcha'),
    }


@lru_cache
def get_settings():
    """读取配置优化写法"""
    return Settings()


settings = get_settings()

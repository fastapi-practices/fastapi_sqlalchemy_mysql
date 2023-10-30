#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=True)

    # Env Config
    ENVIRONMENT: Literal['dev', 'pro']

    # Env MySQL
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    # Env Token
    TOKEN_SECRET_KEY: str  # 密钥 secrets.token_urlsafe(32)

    # FastAPI
    API_V1_STR: str = '/api/v1'
    TITLE: str = 'FastAPI'
    VERSION: str = '0.0.1'
    DESCRIPTION: str = 'FastAPI SQLAlchemy MySQL'
    DOCS_URL: str | None = f'{API_V1_STR}/docs'
    REDOCS_URL: str | None = f'{API_V1_STR}/redocs'
    OPENAPI_URL: str | None = f'{API_V1_STR}/openapi'

    @model_validator(mode='before')
    @classmethod
    def validator_api_url(cls, values):
        if values['ENVIRONMENT'] == 'pro':
            values['OPENAPI_URL'] = None
        return values

    # Static Server
    STATIC_FILE: bool = True

    # Limiter
    LIMITER_REDIS_PREFIX: str = 'fsm_limiter'

    # Uvicorn
    UVICORN_HOST: str = '127.0.0.1'
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = True

    # DB
    DB_ECHO: bool = False
    DB_DATABASE: str = 'fsm'
    DB_CHARSET: str = 'utf8mb4'

    # DateTime
    DATETIME_TIMEZONE: str = 'Asia/Shanghai'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Redis
    REDIS_TIMEOUT: int = 10

    # Captcha
    CAPTCHA_EXPIRATION_TIME: int = 60 * 5  # 过期时间，单位：秒

    # Log
    LOG_STDOUT_FILENAME: str = 'fsm_access.log'
    LOG_STDERR_FILENAME: str = 'fsm_error.log'

    # Token
    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_URL_SWAGGER: str = f'{API_V1_STR}/auth/swagger_login'
    TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3  # 单位：m

    # 中间件
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_GZIP: bool = True
    MIDDLEWARE_ACCESS: bool = False


@lru_cache
def get_settings():
    """读取配置优化写法"""
    return Settings()


settings = get_settings()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from backend.core.conf import settings
from backend.middleware.access_middle import AccessMiddleware


def register_middleware(app: FastAPI) -> None:
    # cors
    if settings.MIDDLEWARE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    # gzip
    if settings.MIDDLEWARE_GZIP:
        app.add_middleware(GZipMiddleware)
    # 接口访问日志
    if settings.MIDDLEWARE_ACCESS:
        app.add_middleware(AccessMiddleware)

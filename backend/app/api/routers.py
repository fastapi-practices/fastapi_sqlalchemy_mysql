#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.user import router as user_router
from backend.app.core.conf import settings

v1 = APIRouter(prefix=settings.API_V1_STR)

v1.include_router(auth_router, prefix='/auth', tags=['认证'])

v1.include_router(user_router, prefix='/users', tags=['用户'])

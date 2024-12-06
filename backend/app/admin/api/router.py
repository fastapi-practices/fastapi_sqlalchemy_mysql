#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.v1.auth import router as auth_router
from backend.app.admin.api.v1.user import router as user_router

v1 = APIRouter()

v1.include_router(auth_router)
v1.include_router(user_router, prefix='/users', tags=['用户'])

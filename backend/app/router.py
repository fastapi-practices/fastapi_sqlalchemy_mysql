#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.api.router import v1 as admin_v1
from backend.core.conf import settings

route = APIRouter()

route.include_router(admin_v1, prefix=settings.FASTAPI_API_V1_PATH)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.admin.service.auth_service import auth_service
from backend.common.security.jwt import DependsJwtAuth
from backend.common.response.response_schema import response_base, ResponseModel, ResponseSchemaModel
from backend.app.admin.schema.token import GetSwaggerToken, GetLoginToken
from backend.app.admin.schema.user import Auth2

router = APIRouter()


@router.post('/login/swagger', summary='swagger 调试专用', description='用于快捷进行 swagger 认证')
async def swagger_login(form_data: OAuth2PasswordRequestForm = Depends()) -> GetSwaggerToken:
    token, user = await auth_service.swagger_login(form_data=form_data)
    return GetSwaggerToken(access_token=token, user=user)  # type: ignore


@router.post('/login', summary='验证码登录')
async def user_login(request: Request, obj: Auth2) -> ResponseSchemaModel[GetLoginToken]:
    data = await auth_service.login(request=request, obj=obj)
    return response_base.success(data=data)


@router.post('/logout', summary='用户登出', dependencies=[DependsJwtAuth])
async def user_logout() -> ResponseModel:
    return response_base.success()

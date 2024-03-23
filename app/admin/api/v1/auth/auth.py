#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from common.jwt import DependsJwtUser
from common.response.response_schema import response_base, ResponseModel
from app.admin.schema.token import Token
from app.admin.schema.user import Auth2
from app.admin.service.user_service import UserService

router = APIRouter()


@router.post('/login/swagger', summary='swagger 表单登录', description='form 格式登录，仅用于 swagger 文档调试接口')
async def swagger_login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token, user = await UserService.login_swagger(form_data=form_data)
    return Token(access_token=token, user=user)  # type: ignore


@router.post('/login', summary='验证码登录')
async def user_login(request: Request, obj: Auth2) -> Token:
    token, user = await UserService.login_captcha(obj=obj, request=request)
    return Token(access_token=token, user=user)  # type: ignore


@router.post('/logout', summary='登出', dependencies=[DependsJwtUser])
async def user_logout() -> ResponseModel:
    return await response_base.success()

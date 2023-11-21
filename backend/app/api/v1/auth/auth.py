#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.common.jwt import DependsJwtUser
from backend.app.common.response.response_schema import response_base
from backend.app.schemas.token import Token
from backend.app.schemas.user import Auth2
from backend.app.services.user_service import UserService

router = APIRouter()


@router.post('/swagger_login', summary='swagger 表单登录', description='form 格式登录，仅用于 swagger 文档调试接口')
async def swagger_user_login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token, user = await UserService.login_swagger(form_data=form_data)
    return Token(access_token=token, user=user)  # type: ignore


@router.post('/login', summary='验证码登录')
async def user_login(request: Request, obj: Auth2) -> Token:
    token, user = await UserService.login_captcha(obj=obj, request=request)
    return Token(access_token=token, user=user)  # type: ignore


@router.post('/logout', summary='登出', dependencies=[DependsJwtUser])
async def user_logout():
    return await response_base.success()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Query

from backend.common.security.jwt import CurrentUser, DependsJwtAuth
from backend.common.pagination import paging_data, DependsPagination, PageData
from backend.common.response.response_schema import response_base, ResponseModel, ResponseSchemaModel
from backend.database.db import CurrentSession
from backend.app.admin.schema.user import CreateUser, GetUserInfo, ResetPassword, UpdateUser, Avatar
from backend.app.admin.service.user_service import UserService
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.post('/register', summary='用户注册')
async def user_register(obj: CreateUser) -> ResponseModel:
    await UserService.register(obj=obj)
    return response_base.success()


@router.post('/password/reset', summary='密码重置', dependencies=[DependsJwtAuth])
async def password_reset(obj: ResetPassword) -> ResponseModel:
    count = await UserService.pwd_reset(obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get('/{username}', summary='查看用户信息', dependencies=[DependsJwtAuth])
async def get_user(username: str) -> ResponseSchemaModel[GetUserInfo]:
    current_user = await UserService.get_userinfo(username=username)
    data = GetUserInfo(**select_as_dict(current_user))
    return response_base.success(data=data)


@router.put('/{username}', summary='更新用户信息', dependencies=[DependsJwtAuth])
async def update_userinfo(username: str, obj: UpdateUser) -> ResponseModel:
    count = await UserService.update(username=username, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{username}/avatar', summary='更新头像', dependencies=[DependsJwtAuth])
async def update_avatar(username: str, avatar: Avatar) -> ResponseModel:
    count = await UserService.update_avatar(username=username, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get(
    '',
    summary='（模糊条件）分页获取所有用户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_all_users(
    db: CurrentSession,
    username: Annotated[str | None, Query()] = None,
    phone: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
) -> ResponseSchemaModel[PageData[GetUserInfo]]:
    user_select = await UserService.get_select(username=username, phone=phone, status=status)
    page_data = await paging_data(db, user_select)
    return response_base.success(data=page_data)


@router.delete(
    path='/{username}',
    summary='用户注销',
    description='用户注销 != 用户登出，注销之后用户将从数据库删除',
    dependencies=[DependsJwtAuth],
)
async def delete_user(current_user: CurrentUser, username: str) -> ResponseModel:
    count = await UserService.delete(current_user=current_user, username=username)
    if count > 0:
        return response_base.success()
    return response_base.fail()

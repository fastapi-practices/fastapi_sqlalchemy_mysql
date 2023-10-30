#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.common.jwt import CurrentUser, DependsJwtUser
from backend.app.common.pagination import PageDepends, paging_data
from backend.app.common.response.response_schema import response_base
from backend.app.database.db_mysql import CurrentSession
from backend.app.schemas.user import CreateUser, GetUserInfo, ResetPassword, UpdateUser, Avatar
from backend.app.services.user_service import UserService
from backend.app.utils.serializers import select_as_dict

router = APIRouter()


@router.post('/register', summary='用户注册')
async def user_register(obj: CreateUser):
    await UserService.register(obj=obj)
    return await response_base.success()


@router.post('/password/reset', summary='密码重置', dependencies=[DependsJwtUser])
async def password_reset(obj: ResetPassword):
    count = await UserService.pwd_reset(obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.get('/{username}', summary='查看用户信息', dependencies=[DependsJwtUser])
async def get_user(username: str):
    current_user = await UserService.get_userinfo(username=username)
    data = GetUserInfo(**await select_as_dict(current_user))
    return await response_base.success(data=data)


@router.put('/{username}', summary='更新用户信息', dependencies=[DependsJwtUser])
async def update_userinfo(username: str, obj: UpdateUser):
    count = await UserService.update(username=username, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.put('/{username}/avatar', summary='更新头像', dependencies=[DependsJwtUser])
async def update_avatar(username: str, avatar: Avatar):
    count = await UserService.update_avatar(username=username, avatar=avatar)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.get('', summary='（模糊条件）分页获取所有用户', dependencies=[DependsJwtUser, PageDepends])
async def get_all_users(
    db: CurrentSession,
    username: Annotated[str | None, Query()] = None,
    phone: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
):
    user_select = await UserService.get_select(username=username, phone=phone, status=status)
    page_data = await paging_data(db, user_select, GetUserInfo)
    return await response_base.success(data=page_data)


@router.put('/{pk}/super', summary='修改用户超级权限', dependencies=[DependsJwtUser])
async def super_set(current_user: CurrentUser, pk: int):
    count = await UserService.update_permission(current_user=current_user, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.put('/{pk}/status', summary='修改用户状态', dependencies=[DependsJwtUser])
async def status_set(current_user: CurrentUser, pk: int):
    count = await UserService.update_status(current_user=current_user, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.delete(
    path='/{username}',
    summary='用户注销',
    description='用户注销 != 用户登出，注销之后用户将从数据库删除',
    dependencies=[DependsJwtUser],
)
async def delete_user(current_user: CurrentUser, username: str):
    count = await UserService.delete(current_user=current_user, username=username)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import Field, EmailStr, ConfigDict, HttpUrl

from backend.common.schema import SchemaBase, CustomPhoneNumber


class AuthSchemaBase(SchemaBase):
    username: str = Field(description='用户名')
    password: str = Field(description='密码')


class AuthLoginParam(AuthSchemaBase):
    captcha: str = Field(description='验证码')


class RegisterUserParam(AuthSchemaBase):
    email: EmailStr = Field(examples=['user@example.com'], description='邮箱')


class UpdateUserParam(SchemaBase):
    username: str = Field(description='用户名')
    email: EmailStr = Field(examples=['user@example.com'], description='邮箱')
    phone: CustomPhoneNumber | None = Field(None, description='手机号')


class AvatarParam(SchemaBase):
    url: HttpUrl = Field(..., description='头像 http 地址')


class GetUserInfoDetail(UpdateUserParam):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='用户 ID')
    uuid: str = Field(description='用户 UUID')
    avatar: str | None = Field(None, description='头像')
    status: int = Field(description='状态')
    is_superuser: bool = Field(description='是否超级管理员')
    join_time: datetime = Field(description='加入时间')
    last_login_time: datetime | None = Field(None, description='最后登录时间')


class ResetPassword(SchemaBase):
    username: str = Field(description='用户名')
    old_password: str = Field(description='旧密码')
    new_password: str = Field(description='新密码')
    confirm_password: str = Field(description='确认密码')

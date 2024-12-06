#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from pydantic import Field, EmailStr, ConfigDict, UUID4, HttpUrl

from backend.common.schema import SchemaBase, CustomPhoneNumber


class Auth(SchemaBase):
    username: str
    password: str


class Auth2(Auth):
    captcha: str


class CreateUser(Auth):
    email: EmailStr = Field(examples=['user@example.com'])


class UpdateUser(SchemaBase):
    username: str
    email: EmailStr = Field(examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None


class Avatar(SchemaBase):
    url: HttpUrl = Field(..., description='头像 http 地址')


class GetUserInfo(UpdateUser):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID4
    status: int
    is_superuser: bool
    avatar: str | None = None
    join_time: datetime.datetime
    last_login_time: datetime.datetime | None = None


class ResetPassword(SchemaBase):
    username: str
    old_password: str
    new_password: str
    confirm_password: str

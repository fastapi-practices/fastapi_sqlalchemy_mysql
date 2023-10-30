#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from email_validator import validate_email, EmailNotValidError
from pydantic import Field, EmailStr, field_validator, ConfigDict, UUID4, HttpUrl

from backend.app.schemas.base import SchemaBase


class Auth(SchemaBase):
    username: str
    password: str


class Auth2(Auth):
    captcha: str


class CreateUser(Auth):
    email: str = Field(..., example='user@example.com')

    @field_validator('email')
    @classmethod
    def email_validate(cls, v: str):
        try:
            validate_email(v, check_deliverability=False).email
        except EmailNotValidError:
            raise ValueError('邮箱格式错误')
        return v


class UpdateUser(SchemaBase):
    username: str
    email: str
    phone: str | None = None

    @field_validator('email')
    @classmethod
    def email_validate(cls, v: str):
        try:
            validate_email(v, check_deliverability=False).email
        except EmailNotValidError:
            raise ValueError('邮箱格式错误')
        return v


class Avatar(SchemaBase):
    url: HttpUrl = Field(..., description='头像 http 地址')


class GetUserInfo(UpdateUser):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID4
    username: str
    email: EmailStr
    status: int
    is_superuser: bool
    avatar: str | None = None
    phone: str | None = None
    join_time: datetime.datetime
    last_login_time: datetime.datetime | None = None


class DeleteUser(SchemaBase):
    id: int


class ResetPassword(SchemaBase):
    username: str
    password1: str
    password2: str

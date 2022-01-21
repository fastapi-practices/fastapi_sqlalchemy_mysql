#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class Auth(BaseModel):
    username: str
    password: str


class CreateUser(Auth):
    email: str = Field(..., example='user@example.com')


class GetUserInfo(CreateUser):
    avatar: str
    mobile_number: int
    we_chart: str
    qq: str
    blog_address: str
    introduction: str


class DeleteUser(BaseModel):
    id: int


class ResetPassword(BaseModel):
    code: str
    password1: str
    password2: str

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.msd.schema import SchemaBase
from app.admin.schema.user import GetUserInfo


class Token(SchemaBase):
    code: int = 200
    msg: str = 'Success'
    access_token: str
    token_type: str = 'Bearer'
    user: GetUserInfo

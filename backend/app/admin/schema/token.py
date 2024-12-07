#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.common.schema import SchemaBase
from backend.app.admin.schema.user import GetUserInfo


class GetSwaggerToken(SchemaBase):
    access_token: str
    token_type: str = 'Bearer'
    user: GetUserInfo


class GetLoginToken(GetSwaggerToken):
    access_token_type: str = 'Bearer'

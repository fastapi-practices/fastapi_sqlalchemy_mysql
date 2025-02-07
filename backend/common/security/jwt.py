#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, ExpiredSignatureError, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from typing_extensions import Annotated

from backend.common.exception.errors import TokenError, AuthorizationError
from backend.core.conf import settings
from backend.database.db import CurrentSession
from backend.app.admin.model.user import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL_SWAGGER)

password_hash = PasswordHash((BcryptHasher(),))


def get_hash_password(password: str, salt: bytes | None) -> str:
    """
    Encrypt passwords using the hash algorithm

    :param password:
    :param salt:
    :return:
    """
    return password_hash.hash(password, salt=salt)


def password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    Password verification

    :param plain_password: The password to verify
    :param hashed_password: The hash ciphers to compare
    :return:
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(sub: str) -> str:
    """
    Generate encryption token

    :param sub: The subject/userid of the JWT
    :return:
    """
    to_encode = {'sub': sub}
    access_token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)
    return access_token


def get_token(request: Request) -> str:
    """
    Get token for request header

    :return:
    """
    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise TokenError(msg='Token 无效')
    return token


def jwt_decode(token: str) -> int:
    """
    Decode token

    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        user_id = int(payload.get('sub'))
        if not user_id:
            raise TokenError(msg='Token 无效')
    except ExpiredSignatureError:
        raise TokenError(msg='Token 已过期')
    except (JWTError, Exception):
        raise TokenError(msg='Token 无效')
    return user_id


async def get_current_user(db: CurrentSession, token: str = Depends(oauth2_schema)) -> User:
    """
    通过 token 获取当前用户

    :param db:
    :param token:
    :return:
    """
    user_id = jwt_decode(token)
    from backend.app.admin.crud.crud_user import user_dao

    user = await user_dao.get(db, user_id)
    if not user:
        raise TokenError(msg='Token 无效')
    if not user.status:
        raise AuthorizationError(msg='用户已被锁定，请联系系统管理员')
    return user


def superuser_verify(user: User):
    """
    验证当前用户是否为超级用户

    :param user:
    :return:
    """
    superuser = user.is_superuser
    if not superuser:
        raise AuthorizationError
    return superuser


# 用户依赖注入
CurrentUser = Annotated[User, Depends(get_current_user)]
# 权限依赖注入
DependsJwtAuth = Depends(get_current_user)

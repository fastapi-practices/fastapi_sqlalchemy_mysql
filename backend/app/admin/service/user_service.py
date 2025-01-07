#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select

from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify, password_verify, get_hash_password
from backend.app.admin.crud.crud_user import user_dao
from backend.database.db import async_db_session
from backend.app.admin.model import User
from backend.app.admin.schema.user import CreateUser, ResetPassword, UpdateUser, Avatar


class UserService:
    @staticmethod
    async def register(*, obj: CreateUser) -> None:
        async with async_db_session.begin() as db:
            if not obj.password:
                raise errors.ForbiddenError(msg='密码为空')
            username = await user_dao.get_by_username(db, obj.username)
            if username:
                raise errors.ForbiddenError(msg='用户已注册')
            email = await user_dao.check_email(db, obj.email)
            if email:
                raise errors.ForbiddenError(msg='邮箱已注册')
            await user_dao.create(db, obj)

    @staticmethod
    async def pwd_reset(*, obj: ResetPassword) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get_by_username(db, obj.username)
            if not password_verify(obj.old_password, user.password):
                raise errors.ForbiddenError(msg='原密码错误')
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg='密码输入不一致')
            new_pwd = get_hash_password(obj.new_password, user.salt)
            count = await user_dao.reset_password(db, user.id, new_pwd)
            return count

    @staticmethod
    async def get_userinfo(*, username: str) -> User:
        async with async_db_session() as db:
            user = await user_dao.get_by_username(db, username)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            return user

    @staticmethod
    async def update(*, username: str, obj: UpdateUser) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_username(db, username=username)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            superuser_verify(input_user)
            if input_user.username != obj.username:
                _username = await user_dao.get_by_username(db, obj.username)
                if _username:
                    raise errors.ForbiddenError(msg='用户名已注册')
            if input_user.email != obj.email:
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='邮箱已注册')
            count = await user_dao.update_userinfo(db, input_user.id, obj)
            return count

    @staticmethod
    async def update_avatar(*, username: str, avatar: Avatar) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            count = await user_dao.update_avatar(db, input_user.id, avatar)
            return count

    @staticmethod
    async def get_select(*, username: str = None, phone: str = None, status: int = None) -> Select:
        return await user_dao.get_list(username=username, phone=phone, status=status)

    @staticmethod
    async def delete(*, current_user: User, username: str) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(current_user)
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            count = await user_dao.delete(db, input_user.id)
            return count

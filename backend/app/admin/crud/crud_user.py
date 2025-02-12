#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import bcrypt
from sqlalchemy import select, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import User
from backend.app.admin.schema.user import CreateUser, UpdateUser, Avatar
from backend.common.security.jwt import get_hash_password


class CRUDUser(CRUDPlus[User]):
    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        """
        获取用户

        :param db:
        :param user_id:
        :return:
        """
        return await self.select_model(db, user_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        通过 username 获取用户

        :param db:
        :param username:
        :return:
        """
        return await self.select_model_by_column(db, username=username)

    async def update_login_time(self, db: AsyncSession, username: str, login_time: datetime) -> int:
        user = await db.execute(
            update(self.model).where(self.model.username == username).values(last_login_time=login_time)
        )
        return user.rowcount

    async def create(self, db: AsyncSession, obj: CreateUser) -> None:
        """
        创建用户

        :param db:
        :param obj:
        :return:
        """
        salt = bcrypt.gensalt()
        obj.password = get_hash_password(obj.password, salt)
        dict_obj = obj.model_dump()
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)
        db.add(new_user)

    async def update_userinfo(self, db: AsyncSession, input_user: int, obj: UpdateUser) -> int:
        """
        更新用户信息

        :param db:
        :param input_user:
        :param obj:
        :return:
        """
        return await self.update_model(db, input_user, obj)

    async def update_avatar(self, db: AsyncSession, input_user: int, avatar: Avatar) -> int:
        """
        更新用户头像

        :param db:
        :param input_user:
        :param avatar:
        :return:
        """
        return await self.update_model(db, input_user, {'avatar': avatar.url})

    async def delete(self, db: AsyncSession, user_id: int) -> int:
        """
        删除用户

        :param db:
        :param user_id:
        :return:
        """
        return await self.delete_model(db, user_id)

    async def check_email(self, db: AsyncSession, email: str) -> User:
        """
        检查邮箱是否存在

        :param db:
        :param email:
        :return:
        """
        return await self.select_model_by_column(db, email=email)

    async def reset_password(self, db: AsyncSession, pk: int, new_pwd: str) -> int:
        """
        重置用户密码

        :param db:
        :param pk:
        :param new_pwd:
        :return:
        """
        return await self.update_model(db, pk, {'password': new_pwd})

    async def get_list(self, username: str = None, phone: str = None, status: int = None) -> Select:
        """
        获取用户列表

        :param username:
        :param phone:
        :param status:
        :return:
        """
        stmt = select(self.model).order_by(desc(self.model.join_time))
        where_list = []
        if username:
            where_list.append(self.model.username.like(f'%{username}%'))
        if phone:
            where_list.append(self.model.phone.like(f'%{phone}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt


user_dao: CRUDUser = CRUDUser(User)

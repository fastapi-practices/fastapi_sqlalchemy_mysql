#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import select, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import User
from backend.common import jwt
from backend.app.admin.schema.user import CreateUser, UpdateUser, Avatar


class CRUDUser(CRUDPlus[User]):
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        return await self.select_model_by_id(db, user_id)

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User | None:
        return await self.select_model_by_column(db, 'username', username)

    async def update_user_login_time(self, db: AsyncSession, username: str, login_time: datetime) -> int:
        user = await db.execute(
            update(self.model).where(self.model.username == username).values(last_login_time=login_time)
        )
        return user.rowcount

    async def create_user(self, db: AsyncSession, create: CreateUser) -> None:
        create.password = await jwt.get_hash_password(create.password)
        new_user = self.model(**create.model_dump())
        db.add(new_user)

    async def update_userinfo(self, db: AsyncSession, current_user: User, obj: UpdateUser) -> int:
        return await self.update_model(db, current_user.id, obj)

    async def update_avatar(self, db: AsyncSession, current_user: User, avatar: Avatar) -> int:
        return await self.update_model(db, current_user.id, {'avatar': avatar.url})

    async def delete_user(self, db: AsyncSession, user_id: int) -> int:
        return await self.delete_model(db, user_id)

    async def check_email(self, db: AsyncSession, email: str) -> User:
        return await self.select_model_by_column(db, 'email', email)

    async def reset_password(self, db: AsyncSession, username: str, password: str) -> int:
        user = await db.execute(
            update(self.model)
            .where(self.model.username == username)
            .values(password=await jwt.get_hash_password(password))
        )
        return user.rowcount

    async def get_all(self, username: str = None, phone: str = None, status: int = None) -> Select:
        se = select(self.model).order_by(desc(self.model.join_time))
        where_list = []
        if username:
            where_list.append(self.model.username.like(f'%{username}%'))
        if phone:
            where_list.append(self.model.phone.like(f'%{phone}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def get_user_super(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.get_user_by_id(db, user_id)
        return user.is_superuser

    async def get_user_status(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.get_user_by_id(db, user_id)
        return user.status

    async def super_set(self, db: AsyncSession, user_id: int) -> int:
        super_status = await self.get_user_super(db, user_id)
        return await self.update_model(db, user_id, {'is_superuser': False if super_status else True})

    async def status_set(self, db: AsyncSession, user_id: int) -> int:
        status = await self.get_user_status(db, user_id)
        return await self.update_model(db, user_id, {'status': False if status else True})


UserDao: CRUDUser = CRUDUser(User)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, NoReturn

from sqlalchemy import func, select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from backend.app.api import jwt
from backend.app.models import User
from backend.app.schemas.user import CreateUser, DeleteUser, UpdateUser


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    user = await db.execute(select(User).where(User.username == username))
    return user.scalars().first()


async def update_user_login_time(db: AsyncSession, username: str) -> int:
    user = await db.execute(
        update(User)
        .where(User.username == username)
        .values(last_login=func.now())
    )
    return user.rowcount


async def get_email_by_username(db: AsyncSession, username: str) -> str:
    user = await get_user_by_username(db, username)
    return user.email


async def get_username_by_email(db: AsyncSession, email: str) -> str:
    user = await db.execute(select(User).where(User.email == email))
    return user.scalars().first().username


async def get_avatar_by_username(db: AsyncSession, username: str) -> str:
    user = await db.execute(select(User).where(User.username == username))
    return user.scalars().first().avatar


async def create_user(db: AsyncSession, create: CreateUser) -> NoReturn:
    create.password = jwt.get_hash_password(create.password)
    new_user = User(**create.dict())
    db.add(new_user)


async def update_userinfo(db: AsyncSession, current_user: User, obj: UpdateUser) -> int:
    user = await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(**obj.dict())
    )
    return user.rowcount


async def update_avatar(db: AsyncSession, current_user: User, avatar: str) -> int:
    user = await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=avatar)
    )
    return user.rowcount


async def delete_user(db: AsyncSession, user_id: DeleteUser) -> int:
    user = await db.execute(delete(User).where(User.id == user_id))
    return user.rowcount


async def check_email(db: AsyncSession, email: str) -> User:
    mail = await db.execute(select(User).where(User.email == email))
    return mail.scalars().first()


async def delete_avatar(db: AsyncSession, user_id: int) -> int:
    user = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(avatar=None)
    )
    return user.rowcount


async def reset_password(db: AsyncSession, username: str, password: str) -> int:
    user = await db.execute(
        update(User)
        .where(User.username == username)
        .values(password=jwt.get_hash_password(password))
    )
    return user.rowcount


def get_users() -> Select:
    return select(User).order_by(desc(User.time_joined))


async def get_user_is_super(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    return user.is_superuser


async def get_user_is_active(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    return user.is_active


async def super_set(db: AsyncSession, user_id: int) -> int:
    super_status = await get_user_is_super(db, user_id)
    user = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_superuser=False if super_status else True)
    )
    return user.rowcount


async def active_set(db: AsyncSession, user_id: int) -> int:
    active_status = await get_user_is_active(db, user_id)
    user = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False if active_status else True)
    )
    return user.rowcount

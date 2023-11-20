#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import DataClassBase, id_key
from backend.app.utils.generate_string import get_uuid4_str
from backend.app.utils.timezone import timezone


class User(DataClassBase):
    """用户表"""

    __tablename__ = 'sys_user'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50), init=False, default_factory=get_uuid4_str, unique=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, comment='用户名')
    password: Mapped[str] = mapped_column(String(255), comment='密码')
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment='邮箱')
    status: Mapped[int] = mapped_column(default=1, comment='用户账号状态(0停用 1正常)')
    is_superuser: Mapped[bool] = mapped_column(default=False, comment='超级权限(0否 1是)')
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment='头像')
    phone: Mapped[str | None] = mapped_column(String(11), default=None, comment='手机号')
    join_time: Mapped[datetime] = mapped_column(init=False, default_factory=timezone.now, comment='注册时间')
    last_login_time: Mapped[datetime | None] = mapped_column(init=False, onupdate=timezone.now, comment='上次登录')

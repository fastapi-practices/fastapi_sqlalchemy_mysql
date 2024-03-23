#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# 导入所有模型，并将 MappedBase 放在最前面， 以便 MappedBase 拥有它们
# imported by Alembic
"""

from common.msd.model import MappedBase
from app.admin.model.user import User

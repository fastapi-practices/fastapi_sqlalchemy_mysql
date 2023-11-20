#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid


def get_uuid4_str() -> str:
    """
    获取 uuid4 字符串

    :return:
    """
    return str(uuid.uuid4())

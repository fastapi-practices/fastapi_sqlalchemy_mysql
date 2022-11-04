#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Any, Union, Set, Dict

from fastapi.encoders import jsonable_encoder
from pydantic import validate_arguments, BaseModel

_JsonEncoder = Union[Set[Union[int, str]], Dict[Union[int, str], Any]]

__all__ = [
    'ResponseModel',
    'response_base'
]


class ResponseModel(BaseModel):
    """
    统一返回模型, 可以在 FastAPI 接口请求中使用 response_model=ResponseModel 及更多操作, 前提是当它是一个非 200 响应时
    """
    code: int
    msg: str
    data: Optional[Any] = None


class ResponseBase:

    @staticmethod
    def __encode_json(data: Any):
        return jsonable_encoder(
            data,
            custom_encoder={
                # datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S")  # 格式化时区时间
            }
        )

    @staticmethod
    @validate_arguments
    def success(*, code: int = 200, msg: str = 'Success', data: Optional[Any] = None,
                exclude: Optional[_JsonEncoder] = None):
        """
        请求成功返回通用方法

        :param code: 返回状态码
        :param msg: 返回信息
        :param data: 返回数据
        :param exclude: 排除返回数据(data)字段
        :return:
        """
        return ResponseModel(code=code, msg=msg, data=ResponseBase.__encode_json(data)).dict(exclude={'data': exclude})

    @staticmethod
    @validate_arguments
    def fail(*, code: int = 400, msg: str = 'Bad Request', data: Any = None):
        return ResponseModel(code=code, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_200(*, msg: str = 'Success', data: Optional[Any] = None, exclude: Optional[_JsonEncoder] = None):
        return ResponseModel(code=200, msg=msg, data=ResponseBase.__encode_json(data)).dict(exclude={'data': exclude})


response_base = ResponseBase()

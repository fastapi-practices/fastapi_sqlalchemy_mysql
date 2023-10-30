#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asgiref.sync import sync_to_async
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.errors import PydanticUserError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from backend.app.common.exception.errors import BaseExceptionMixin
from backend.app.common.log import log
from backend.app.common.response.response_schema import response_base
from backend.app.core.conf import settings
from backend.app.schemas.base import (
    convert_validation_errors,
    CUSTOM_VALIDATION_ERROR_MESSAGES,
    convert_usage_errors,
    CUSTOM_USAGE_ERROR_MESSAGES,
)


@sync_to_async
def _get_exception_code(status_code):
    """
    获取返回状态码, OpenAPI, Uvicorn... 可用状态码基于 RFC 定义, 详细代码见下方链接

    `python 状态码标准支持 <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http
    /__init__.py#L7>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__

    :param status_code:
    :return:
    """
    try:
        STATUS_PHRASES[status_code]
    except Exception:
        code = 400
    else:
        code = status_code
    return code


async def _validation_exception_handler(e: RequestValidationError | ValidationError):
    """
    数据验证异常处理

    :param e:
    :return:
    """

    message = ''
    errors = await convert_validation_errors(e, CUSTOM_VALIDATION_ERROR_MESSAGES)
    for error in errors[:1]:
        if error.get('type') == 'json_invalid':
            message += 'json解析失败'
        else:
            error_input = error.get('input')
            ctx = error.get('ctx')
            ctx_error = ctx.get('error') if ctx else None
            field = str(error.get('loc')[-1])
            error_msg = error.get('msg')
            message += f'{field} {ctx_error if ctx else error_msg}: {error_input}' + '.'
    content = {
        'code': 422,
        'msg': '请求参数非法' if len(message) == 0 else f'请求参数非法: {message}',
        'data': {'errors': e.errors()} if message == '' and settings.UVICORN_RELOAD is True else None,
    }
    return JSONResponse(status_code=422, content=await response_base.fail(**content))


def register_exception(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        全局HTTP异常处理

        :param request:
        :param exc:
        :return:
        """
        content = {'code': exc.status_code, 'msg': exc.detail}
        request.state.__request_http_exception__ = content  # 用于在中间件中获取异常信息
        return JSONResponse(
            status_code=await _get_exception_code(exc.status_code),
            content=await response_base.fail(**content),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        fastapi 数据验证异常处理

        :param request:
        :param exc:
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """
        pydantic 数据验证异常处理

        :param request:
        :param exc:
        :return:
        """
        return await _validation_exception_handler(exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """
        Pydantic 用户异常处理

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=500,
            content=await response_base.fail(
                code=exc.code, msg=await convert_usage_errors(exc, CUSTOM_USAGE_ERROR_MESSAGES)
            ),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        全局异常处理

        :param request:
        :param exc:
        :return:
        """
        if isinstance(exc, BaseExceptionMixin):
            return JSONResponse(
                status_code=await _get_exception_code(exc.code),
                content=await response_base.fail(code=exc.code, msg=str(exc.msg), data=exc.data if exc.data else None),
                background=exc.background,
            )

        elif isinstance(exc, AssertionError):
            return JSONResponse(
                status_code=500,
                content=await response_base.fail(
                    code=500,
                    msg=','.join(exc.args)
                    if exc.args
                    else exc.__repr__()
                    if not exc.__repr__().startswith('AssertionError()')
                    else exc.__doc__,
                )
                if settings.ENVIRONMENT == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
            )

        else:
            import traceback

            log.error(f'未知异常: {exc}')
            log.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content=await response_base.fail(code=500, msg=str(exc))
                if settings.ENVIRONMENT == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
            )

    if settings.MIDDLEWARE_CORS:

        @app.exception_handler(500)
        async def cors_status_code_500_exception_handler(request, exc):
            """
            跨域 500 异常处理

            `Related issue <https://github.com/encode/starlette/issues/1175>`_

            :param request:
            :param exc:
            :return:
            """
            response = JSONResponse(
                status_code=exc.code if isinstance(exc, BaseExceptionMixin) else 500,
                content={'code': exc.code, 'msg': exc.msg, 'data': exc.data}
                if isinstance(exc, BaseExceptionMixin)
                else await response_base.fail(code=500, msg=str(exc))
                if settings.ENVIRONMENT == 'dev'
                else await response_base.fail(code=500, msg='Internal Server Error'),
                background=exc.background if isinstance(exc, BaseExceptionMixin) else None,
            )
            origin = request.headers.get('origin')
            if origin:
                cors = CORSMiddleware(
                    app=app, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*']
                )
                response.headers.update(cors.simple_headers)
                has_cookie = 'cookie' in request.headers
                if cors.allow_all_origins and has_cookie:
                    response.headers['Access-Control-Allow-Origin'] = origin
                elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers.add_vary_header('Origin')
            return response

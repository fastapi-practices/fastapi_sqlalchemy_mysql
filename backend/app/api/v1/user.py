#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
from hashlib import sha256
from typing import Optional

from email_validator import EmailNotValidError, validate_email
from fast_captcha import tCaptcha
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, status, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.api import jwt_security
from backend.app.api.jwt_security import create_access_token, get_current_user
from backend.app.common.log import log
from backend.app.core.conf import settings
from backend.app.core.path_conf import ImgPath
from backend.app.crud import user_crud
from backend.app.datebase.db_mysql import get_db
from backend.app.model import User
from backend.app.schemas import Response200, Response403, Response500
from backend.app.schemas.sm_token import Token
from backend.app.schemas.sm_user import CreateUser, GetUserInfo, ResetPassword, Auth
from backend.app.utils.send_email_verification_code import send_email_verification_code

user = APIRouter()

headers = {"WWW-Authenticate": "Bearer"}


@user.post('/login_to_test', summary='用户登录调试', description='form_data登录，配合swagger-ui认证使用，前后端分离直接使用 /login 接口',
           response_model=Token, deprecated=False)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    current_user = user_crud.get_user_by_username(db, form_data.username)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户名不存在', headers=headers)
    elif not jwt_security.verity_password(form_data.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='密码错误', headers=headers)
    elif not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='该用户已被锁定，无法登录', headers=headers)
    # 更新登陆时间
    user_crud.update_user_login_time(db, form_data.username)
    # 创建token
    access_token = create_access_token(current_user.id)
    log.success('用户 [{}] 登陆成功', form_data.username)
    return Token(code=200, msg='登陆成功', access_token=access_token, token_type='Bearer',
                 is_superuser=current_user.is_superuser)


@user.post('/login', summary='用户登录', description='json_data登录', response_model=Token)
async def user_login(user_info: Auth, db: Session = Depends(get_db)):
    current_user = user_crud.get_user_by_username(db, user_info.username)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户名不存在', headers=headers)
    elif not jwt_security.verity_password(user_info.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='密码错误', headers=headers)
    elif not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='该用户已被锁定，无法登录', headers=headers)
    # 更新登陆时间
    user_crud.update_user_login_time(db, user_info.username)
    # 创建token
    access_token = create_access_token(current_user.id)
    log.success('用户 [{}] 登陆成功', user_info.username)
    return Token(code=200, msg='登陆成功', access_token=access_token, token_type='Bearer',
                 is_superuser=current_user.is_superuser)


@user.post('/logout', summary='用户退出')
async def logout(current_user=Depends(get_current_user)):
    if current_user:
        return Response200(msg='退出登录成功')
    Response500(msg='退出登陆失败')


@user.post('/register', summary='用户注册')
async def user_register(create: CreateUser, db: Session = Depends(get_db)):
    username = user_crud.get_user_by_username(db, create.username)
    if username:
        raise HTTPException(status_code=403, detail='该用户名已被注册~ 换一个吧')
    email = db.query(User).filter(User.email == create.email).first()
    if email:
        raise HTTPException(status_code=403, detail='该邮箱已被注册~ 换一个吧')
    try:
        validate_email(create.email).email
    except EmailNotValidError:
        raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    new_user = user_crud.create_user(db, create)
    if new_user:
        log.success('用户 %s 注册成功' % create.username)
        return Response200(msg='用户注册成功', data={
            'username': new_user.username,
            'email': new_user.email
        })
    log.error('用户 %s 注册失败' % create.username)
    return Response500(msg='用户注册失败')


@user.post('/password_reset_code', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_code(username_or_email: str, response: Response, tasks: BackgroundTasks,
                              db: Session = Depends(get_db)):
    code = tCaptcha()
    if user_crud.get_user_by_username(db, username_or_email):
        try:
            response.delete_cookie(key='fast-code')
            response.delete_cookie(key='fast-username')
            response.set_cookie(key='fast-code', value=sha256(code.encode('utf-8')).hexdigest(),
                                max_age=settings.MAX_AGE)
            response.set_cookie(key='fast-username', value=username_or_email, max_age=settings.MAX_AGE)
        except Exception as e:
            log.exception('无法发送验证码 {}', e)
            raise HTTPException(status_code=500, detail='内部错误，无法发送验证码')
        try:
            current_user_email = user_crud.get_email_by_username(db, username_or_email)
            tasks.add_task(send_email_verification_code, current_user_email, code)
        except Exception as e:
            log.exception('验证码发送失败 {}', e)
            raise HTTPException(status_code=500, detail='内部错误，验证码发送失败')
        return Response200(msg='验证码发送成功')
    else:
        try:
            validate_email(str(username_or_email))
        except EmailNotValidError:
            raise HTTPException(status_code=404, detail='用户名不存在，请重新输入')
        email_result = user_crud.check_email(db, username_or_email)
        if not email_result:
            raise HTTPException(status_code=404, detail='邮箱不存在，请重新输入~')
        try:
            response.delete_cookie(key='fast-code')
            response.delete_cookie(key='fast-username')
            response.set_cookie(key='fast-code', value=sha256(code.encode('utf-8')).hexdigest(),
                                max_age=settings.MAX_AGE)
            username = user_crud.get_username_by_email(db, username_or_email)
            response.set_cookie(key='fast-username', value=username, max_age=settings.MAX_AGE)
        except Exception as e:
            log.exception('无法发送验证码 {}', e)
            raise HTTPException(status_code=500, detail='内部错误，无法发送验证码')
        try:
            tasks.add_task(send_email_verification_code, username_or_email, code)
        except Exception as e:
            log.exception('验证码发送失败 {}', e)
            raise HTTPException(status_code=500, detail='内部错误，验证码发送失败')
        return Response200(msg='验证码发送成功')


@user.post('/password_reset_req', summary='密码重置请求')
async def password_reset(resetpwd: ResetPassword, request: Request, response: Response,
                         db: Session = Depends(get_db)):
    pwd1 = resetpwd.password1
    pwd2 = resetpwd.password2
    if pwd1 != pwd2:
        raise HTTPException(status_code=403, detail='两次密码输入不一致，请重新输入~')
    if request.cookies.get('code') != sha256(resetpwd.code.encode('utf-8')).hexdigest():
        raise HTTPException(status_code=403, detail='验证码错误')
    if request.cookies.get('fast-username') is None:
        raise HTTPException(status_code=404, detail='cookie已失效，请重新获取验证码')
    try:
        user_crud.reset_password(db, request.cookies.get('fast-username'), resetpwd.password2)
    except Exception as e:
        log.exception('密码重置失败 {}', e)
        raise HTTPException(status_code=500, detail='内部错误，密码重置失败')
    response.delete_cookie(key='fast-code')
    response.delete_cookie(key='fast-username')
    return Response200(msg='密码重置成功')


@user.get('/password_reset_done', summary='重置密码完成')
async def password_reset_done():
    return {'msg': '密码重置成功'}


@user.get('/userinfo', summary='查看用户信息')
async def userinfo(current_user: GetUserInfo = Depends(get_current_user)):
    if current_user:
        return Response200(msg='查看用户信息成功', data=current_user)


@user.put('/update_userinfo', summary='更新用户信息')
async def update_userinfo(new_username: str,
                          email: str,
                          mobile_number: Optional[int] = None,
                          we_chart: Optional[str] = None,
                          qq: Optional[str] = None,
                          blog_address: Optional[str] = None,
                          introduction: Optional[str] = None,
                          file: UploadFile = File(None),
                          current_user=Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if current_user.username == new_username:
        pass
    else:
        username = user_crud.get_user_by_username(db, new_username)
        if username:
            raise HTTPException(status_code=403, detail='该用户名已存在~ 换一个吧')
    if current_user.email == email:
        pass
    else:
        email = db.query(User).filter(User.email == email).first()
        if email:
            raise HTTPException(status_code=403, detail='该邮箱已存在~ 换一个吧')
        try:
            validate_email(str(email))
        except EmailNotValidError:
            raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    current_filename = user_crud.get_avatar_by_username(db, current_user.username)
    if file is not None:
        if current_filename is not None:
            try:
                os.remove(ImgPath + current_filename)
            except Exception:
                log.warning(f'删除图片:{current_filename}失败，未在本地找到相关图片')
        f = await file.read()
        if 'image' not in file.content_type:
            raise HTTPException(status_code=403, detail='图片格式错误，请重新选择图片')
        filename = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')) + '_' + file.filename
        with open(ImgPath + f'{filename}', 'wb') as ff:
            ff.write(f)
    else:
        filename = current_filename
    if current_user:
        user_crud.update_userinfo(db, current_user, new_username, email, filename, mobile_number, we_chart, qq,
                                  blog_address, introduction)
        return Response200(msg='用户信息更新成功', data={
            'username': new_username,
            'email': email,
            'avatar': filename,
            'mobile_number': mobile_number,
            'we_chart': we_chart,
            'qq': qq,
            'blog_address': blog_address,
            'introduction': introduction,
        })
    return Response500(msg='用户信息更新失败')


@user.get('/user_list', summary='获取用户列表')
async def get_user_list(current_user: GetUserInfo = Depends(jwt_security.get_current_is_superuser),
                        db: Session = Depends(get_db)):
    if current_user:
        user_list = user_crud.get_users(db)
        if user_list:
            return Response200(msg='获取用户信息列表成功', data=user_list)
        return Response500(msg='获取用户信息列表失败')


@user.post('/user_super_set', summary='修改用户超级权限')
async def super_set(user_id: int, current_user=Depends(jwt_security.get_current_is_superuser),
                    db: Session = Depends(get_db)):
    if current_user:
        if user_crud.get_user_by_id(db, user_id):
            if user_crud.super_set(db, user_id):
                return Response200(msg=f'修改超级权限成功，当前：{user_crud.get_user_is_super(db, user_id)}')
            return Response200(msg=f'修改超级权限成功，当前：{user_crud.get_user_is_super(db, user_id)}')
        return Response403(msg='用户不存在')


@user.post('/user_action_set', summary='修改用户状态')
async def active_set(user_id: int, current_user=Depends(jwt_security.get_current_is_superuser),
                     db: Session = Depends(get_db)):
    if current_user:
        if user_crud.get_user_by_id(db, user_id):
            if user_crud.active_set(db, user_id):
                return Response200(msg=f'修改用户状态成功, 当前：{user_crud.get_user_is_action(db, user_id)}')
            return Response200(msg=f'修改用户状态成功, 当前：{user_crud.get_user_is_action(db, user_id)}')
        return Response403(msg='用户不存在')


@user.delete('/user_delete', summary='用户注销', description='用户注销 != 用户退出，注销之后用户将从数据库删除')
async def user_delete(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user:
        try:
            current_filename = user_crud.get_avatar_by_username(db, current_user.username)
            os.remove(ImgPath + current_filename)
        except FileExistsError:
            log.warning(f'删除图片:{current_filename}失败，未在本地找到相关图片')
        finally:
            if not user_crud.delete_user(db, current_user.id):
                return Response200(msg='用户注销成功')
            return Response500(msg='用户注销失败')

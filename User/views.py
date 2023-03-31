import json
from django.http import HttpRequest, HttpResponse

from User.models import Entity, Department, User
from Asset.models import AssetClass, Asset, PendingRequests
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.sessions import *
from utils.manipulate_database import *
from rest_framework.request import Request
from utils.utils_other import *


def check_for_user_data(body):
    name = require(body, "UserName", "string",
                   err_msg="Missing or error type of [name]")
    hashed_password = require(
        body, "Password", "string", err_msg="Missing or error type of [password]")
    assert 0 < len(name) <= 128, "Bad length of [name]"
    assert 0 < len(hashed_password) <= 32, "Bad length of [password]"
    return name, hashed_password


@CheckRequire
def login(req: Request):
    if req.method == 'POST':
        
        # TODO: bugfix
        # if req.user: 
        #     return request_failed(1, "用户已登录") 
        
        tmp_body = req.body.decode("utf-8")
        try:
            body = json.loads(tmp_body) 
        except BaseException as error:
            print(error, tmp_body)
        
        name, hashed_password = check_for_user_data(body)

        # 再进行sha256加密
        sha_hashed_password = sha256(hashed_password)

        user = User.objects.filter(name=name).first()
        if not user:
            return request_failed(2, "用户名或密码错误")
        else:
            print("__", user.name)
            print("__", user.password)
            print("__", sha_hashed_password)
            if user.password == sha_hashed_password:
                session_id = get_session_id(req)
                bind_session_id(sessionId=session_id, user=user)
                print("successfully bind session id!")
                return request_success()
            else:
                return request_failed(3, "用户名或密码错误")
    else:
        return BAD_METHOD

def logout(req: Request):
    
    # TODO
    # 验证是否存在user
    if req.method == 'POST':

        session_id = get_session_id(req)
        disable_session_id(sessionId=session_id)
        return request_success()
    else:
        return BAD_METHOD

def user_info(req: Request):
    if req.method == 'GET':
        # 获取session id
        sessionId = get_session_id(req)

        sessionRecord =SessionPool.objects.filter(sessionId=sessionId).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=sessionId).delete()
                return request_failed(2, "session id expire")
            else:
                usr = sessionRecord.user
                usr_info = {}
                usr_info["UserName"] = usr.name
                if usr.super_administrator == 1:
                    usr_info["Authority"] = 0
                elif usr.system_administrator == 1:
                    usr_info["Authority"] = 1
                elif usr.asset_administrator == 1:
                    usr_info["Authority"] = 2
                else:
                    usr_info["Authority"] = 3
                
                

        else:
            return request_failed(1, "session id doesn't exist")

    else:
        return BAD_METHOD
    


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
        hashed_password = sha256(hashed_password)

        user = User.objects.filter(name=name).first()
        if not user:
            return request_failed(2, "用户名或密码错误")
        else:
            if user.password == hashed_password:
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
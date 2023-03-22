import json
from django.http import HttpRequest, HttpResponse

from User.models import Entity,Department, User
from Asset.models import AssetClass, Asset, PendingRequests
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp


@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")


def check_for_user_data(body):
    name = require(body, "name", "string",
                   err_msg="Missing or error type of [name]")
    hashed_password = require(
        body, "hashed_password", "string", err_msg="Missing or error type of [password]")
    assert 0 < len(name) <= 128, "Bad length of [name]"
    assert 0 < len(hashed_password) <= 32, "Bad length of [password]"
    return name, hashed_password


@CheckRequire
def login(req: HttpRequest):
    if req.method == 'POST':
        if req.user:
            return request_failed(1, {"用户已登录"})
        body = json.loads(req.body.decode("gbk"))
        name, hashed_password = check_for_user_data(body)
        user = User.objects.filter(name=name).first()
        if not user:
            return request_failed(2, {"无效的用户名"})
        else:
            if user.password == hashed_password:
                return request_success({"登录成功，欢迎来到资产管理系统"})
            else:
                return request_failed(2, {"密码错误"})
    else:
        return BAD_METHOD

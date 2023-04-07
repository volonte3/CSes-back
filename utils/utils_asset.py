from Asset.models import AssetClass
from User.models import Department,User
from User.models import SessionPool
from rest_framework.request import Request
from utils.sessions import get_session_id
from utils.utils_other import *
from utils.config import *
from utils.utils_request import *
import json
import pytz
import datetime as dt
from CS_Company_backend.settings import TIME_ZONE

# 鉴权函数
def check_authority(authority_level, usr:User):
    # TODO 
    if authority_level == ONLY_SUPER_ADMIN:
        if usr.super_administrator == 1:
            return None
        else:
            return request_failed(3, "非超级管理员，没有对应权限")
    if authority_level == ONLY_ASSET_ADMIN:
        if usr.asset_administrator == 1:
            return None
        else:
            return request_failed(3, "非资产管理员，没有对应权限")
    return None

def parse_data(request, data_require):
    if (request.method == "POST") or (request.method == "PUT"):
        tmp_body = request.body.decode("utf-8")
        
        try:
            body = json.loads(tmp_body) 
        except BaseException as error:
            print("During get_session_id: ", error, tmp_body)

        data = return_field(body, data_require)

        return data

def AssetWarpper(req, function, authority_level=None, data_require=None, validate_data=None, data_pass=None):

    if (req.method == 'POST') or (req.method == 'PUT'):
        session_id = get_session_id(req)
        # print(session_id)
    
        # 下面是 session_id to user的过程
        sessionRecord =SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(2, "session id expire")
            else:
                usr = sessionRecord.user

                # 检查权限
                check_error = check_authority(authority_level, usr)
                if check_error != None:
                    return check_error
                
                # 从req中解析出数据
                if data_require != None:
                    data = parse_data(req, data_require)
                else:
                    data = None

                # 检查数据是否合理有效, 再传一个 validate_data 函数进来
                if(validate_data != None):
                    data_error = validate_data(data)
                    if data_error != None:
                        return data_error

                return function(usr, data)           
        else:
            return request_failed(1, "session id do not exist")
    
    elif req.method == 'DELETE':
        session_id = data_pass["session_id"]

        # 下面是 session_id to user的过程
        sessionRecord =SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(2, "session id expire")
            else:
                usr = sessionRecord.user

                # 检查权限
                check_error = check_authority(authority_level, usr)
                if check_error != None:
                    return check_error
                
                # 检查数据是否合理有效, 再传一个 validate_data 函数进来
                if(validate_data != None):
                    data_error = validate_data(data_pass)
                    if data_error != None:
                        return data_error

                return function(usr, data_pass)           
        else:
            return request_failed(1, "session id do not exist")
    
    else:
        return BAD_METHOD


def get_department(department_id):
    department = Department.objects.filter(id=department_id)
    assert department != None, "Department NOT Found!"
    return department

def get_asset_class(asset_class_id):
    asset_class = AssetClass.objects.filter(id=asset_class_id).first()
    assert asset_class != None, "Asset Class NOT Found!"
    return asset_class


def give_subtree_recursive(asset_class_id, department_id):
    nodeData = {}

    # 把这个asset_class的title与value填写到nodeData中, value直接写asset_class_id
    asset_class = get_asset_class(asset_class_id)
    assert asset_class.department.id == department_id, "department id is wrong!"

    nodeData['title'] = asset_class.name
    nodeData['value'] = asset_class_id

    # 解析出children_list
    children_list = parse_children(asset_class.children)

    # 如果这个asset_class没有children, 直接返回nodeData
    if len(children_list)==0:
        return nodeData 

    # 如果这个asset_class有children
    children = []
    for child_id in children_list:
        children.append(give_subtree_recursive(child_id, department_id))

    nodeData["children"] = children

    return nodeData

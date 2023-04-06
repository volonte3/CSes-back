from Asset.models import AssetClass
from User.models import Department
from User.models import SessionPool
from rest_framework.request import Request
from utils.sessions import get_session_id
from utils.utils_other import *
from utils.utils_request import BAD_METHOD, request_failed
import pytz
import datetime as dt
from CS_Company_backend.settings import TIME_ZONE

# 可以多写一个鉴定用户是不是资产管理、有没有权限修改的函数
def check_authority(authority_level):
    # TODO 
    # 可以用宏定义,更加清晰一些
    return None

def session_id_to_user(req, function, authority_level, data=None):

    if req.method == 'POST':
        session_id = get_session_id(req)
    
        # 下面是 session_id to user的过程
        sessionRecord =SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(2, "session id expire")
            else:
                usr = sessionRecord.user

                # TODO
                check_result = check_authority(authority_level)
                if check_result != None:
                    return check_result
                
                # TODO:从req中解析出数据
                # 使用return field

                return function(usr, data)           
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

def parse_children(children_string):
    # 这里要不要增加children_string==None的一个判断
    children_list = children_string.split('$')
    return children_list[1:]  # 去除最前面的一个空格

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

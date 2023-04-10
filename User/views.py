import json
from django.http import HttpRequest, HttpResponse

from User.models import Entity, Department, User
from Asset.models import AssetClass, Asset, PendingRequests
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.sessions import *
# from utils.manipulate_database import *
from rest_framework.request import Request
from utils.utils_other import *
from utils.utils_add_data import *


def add_data(req: Request):
    # 增加数据接口
    add_user_class_1()
    return HttpResponse("Congratulations! You have successfully added many data. Go ahead!")


def delete_data(req: Request):
    # 删除数据接口
    delete_user_class_1()
    return HttpResponse("Congratulations! You have successfully deleted many data. Go ahead!")


def check_for_user_data(body):
    name = require(body, "UserName", "string",
                   err_msg="Missing or error type of name")
    hashed_password = require(body, "Password", "string",
                              err_msg="Missing or error type of password")
    assert 0 < len(name) <= 128, "Bad length of name"
    assert 0 < len(hashed_password) <= 32, "Bad length of password"
    return name, hashed_password


@CheckRequire
def login(req: Request):
    if req.method == 'POST':
        # 约定：同一用户可以同时在第二个设备上可以成功登录，但会顶掉第一个设备上的sessionid
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
            if user.Is_Locked:
                return request_failed(4,"用户已被锁定")
            elif user.password == sha_hashed_password:
                session_list = SessionPool.objects.filter(user=user).all()
                if len(session_list) > 0:
                    for session in session_list:
                        SessionPool.objects.filter(sessionId=session.sessionId).delete()
                session_id = get_session_id(req)
                bind_session_id(sessionId=session_id, user=user)
                print("successfully bind session id!")
                return request_success()
            else:
                return request_failed(3, "用户名或密码错误")
    else:
        return BAD_METHOD


def logout(req: Request):
    if req.method == 'POST':
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            disable_session_id(sessionId=session_id)
            return request_success()
        else:
            return request_failed(1, "session id doesn't exist")
    else:
        return BAD_METHOD


def user_info(req: Request, sessionId: str):
    print("调用了user_info函数", sessionId)
    if req.method == 'GET':
        sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
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
                usr_info["UserApp"] = usr.function_string
                return request_success(usr_info)
        else:
            return request_failed(1, "session id doesn't exist")
    else:
        return BAD_METHOD


def get_all_member(req: Request, sessionId: str):
    print("调用了get_all_member函数", sessionId)
    if req.method == "GET":
        sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=sessionId).delete()
                return request_failed(2, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(1, "no permissions")
                else:
                    e1 = user.entity
                    member_list = list(User.objects.filter(entity=e1).all())
                    return_data = {
                        "member":[
                            return_field(member.serialize(),["Name","Department","Authority","lock"])
                        for member in member_list 
                        if member.super_administrator == 0 and member.system_administrator == 0]
                    }
                    return request_success(return_data)
        else:
            return request_failed(2, "session id doesn't exist")
    else:
        return BAD_METHOD
    

def add_member(req: Request):
    print("调用了add_member函数")
    if req.method == "POST":
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    tmp_body = req.body.decode("utf-8")
                    try:
                        body = json.loads(tmp_body)
                    except BaseException as error:
                        print(error, tmp_body)
                    member_name = require(body, "UserName", "string",
                                          err_msg="Missing or error type of UserName")
                    department_path = require(body, "Department","string",
                                              err_msg="Missing or error type of Department")
                    member1 = User.objects.filter(name=member_name).first()
                    if member1:
                        return request_failed(1,"用户名已存在")
                    d1 = Department.objects.filter(path=department_path,entity=e1).first()
                    if not d1:
                        return request_failed(4,"部门不存在")
                    else:
                        if len(parse_children(d1.children)) != 0:
                            return request_failed(4,"不是叶子部门")
                        else:
                            User.objects.create(name=member_name,password=sha256(MD5("yiqunchusheng")),
                                                entity=e1,department=d1,
                                                super_administrator=0,system_administrator=0,asset_administrator=0,
                                                function_string="1111100000000000000000")
                            return request_success()
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD


def remove_member(req:Request, sessionId:str, UserName:str):
    print("调用了remove_member函数")
    print(sessionId)
    print(UserName)
    if req.method == "DELETE":
        sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=sessionId).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    member1 = User.objects.filter(name=UserName,entity=e1).first()
                    if not member1:
                        return request_failed(1,"用户不存在")
                    elif member1.system_administrator == 1:
                        return request_failed(1,"不能删除系统管理员")
                    else:
                        member1.delete()
                        return request_success()
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD


def lock_member(req:Request):
    print("调用了lock_member函数")
    if req.method == "PUT":
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    tmp_body = req.body.decode("utf-8")
                    try:
                        body = json.loads(tmp_body)
                    except BaseException as error:
                        print(error, tmp_body)
                    member_name = require(body, "UserName", "string",
                                          err_msg="Missing or error type of UserName")
                    member = User.objects.filter(name=member_name,entity=e1).first()
                    if not member:
                        return request_failed(1,"用户不存在")
                    else:
                        if member.system_administrator == 1:
                            return request_failed(1,"不能锁定系统管理员")
                        else:
                            member.Is_Locked = not member.Is_Locked
                            member.save()
                            return request_success()
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD


def change_authority(req:Request):
    print("调用了change_authority函数")
    if req.method == "PUT":
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    tmp_body = req.body.decode("utf-8")
                    try:
                        body = json.loads(tmp_body)
                    except BaseException as error:
                        print(error, tmp_body)
                    member_name = require(body, "UserName", "string",
                                          err_msg="Missing or error type of UserName")
                    authority = require(body,"Authority","int",
                                        err_msg="Missing or error type of Authority")
                    member = User.objects.filter(name=member_name,entity=e1).first()
                    if not member:
                        return request_failed(1,"用户不存在")
                    else:
                        if member.system_administrator == 1:
                            return request_failed(1,"不能更改系统管理员的权限")
                        else:
                            if authority == 2:
                                member.super_administrator = 0
                                member.system_administrator = 0
                                member.asset_administrator = 1
                                member.function_string = "0000011111111100000000"
                                member.save()
                                return request_success()
                            elif authority == 3:
                                member.super_administrator = 0
                                member.system_administrator = 0
                                member.asset_administrator = 0
                                member.function_string = "1111100000000000000000"
                                member.save()
                                return request_success()
                            else:
                                return request_failed(2,"无权更改为其他身份")
                            
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD


def remake_password(req:Request):
    print("调用了remake_password函数")
    if req.method == "POST":
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    tmp_body = req.body.decode("utf-8")
                    try:
                        body = json.loads(tmp_body)
                    except BaseException as error:
                        print(error, tmp_body)
                    member_name = require(body, "UserName", "string",
                                          err_msg="Missing or error type of UserName")
                    member = User.objects.filter(name=member_name,entity=e1).first()
                    if not member:
                        return request_failed(1,"用户不存在")
                    else:
                        if member.system_administrator == 1:
                            return request_failed(1,"不能重置系统管理员的密码")
                        else:
                            member.password = sha256(MD5("yiqunchusheng"))
                            member.save()
                            return request_success()
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD


def add_department(req: Request):
    print("调用了add_department函数")
    if req.method == "POST":
        session_id = get_session_id(req)
        sessionRecord = SessionPool.objects.filter(sessionId=session_id).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=session_id).delete()
                return request_failed(5, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(4, "no permissions")
                else:
                    e1 = user.entity
                    tmp_body = req.body.decode("utf-8")
                    try:
                        body = json.loads(tmp_body)
                    except BaseException as error:
                        print(error, tmp_body)
                    DepartmentPath = require(body, "DepartmentPath", "string",
                                             err_msg="Missing or error type of DepartmentPath")
                    DepartmentName = require(body, "DepartmentName", "string",
                                             err_msg="Missing or error type of DepartmentName")
                    d1 = Department.objects.filter(name=DepartmentName,entity=e1).first()
                    if d1:
                        return request_failed(1, "部门名已存在")
                    elif DepartmentPath == '000000000':
                        root_num = len(Department.objects.filter(parent=None,entity=e1).all())
                        if root_num >= 9:
                            return request_failed(3, "部门数已达到上限")
                        else:
                            new_departmentpath = DepartmentPath
                            tmp_list = list(new_departmentpath)
                            tmp_list[0] = str((1 + root_num))
                            new_departmentpath = ''.join(tmp_list)
                            new_d = Department.objects.create(entity=e1, 
                                                              name=DepartmentName,
                                                              path=new_departmentpath)
                            return_data = {
                                    "department_path" : new_departmentpath
                                }
                            return request_success(return_data)
                    else:
                        d2 = Department.objects.filter(path=DepartmentPath,entity=e1).first()
                        if not d2:
                            return request_failed(2, "部门路径无效")
                        else:
                            children_list = parse_children(d2.children)
                            child_num = len(children_list)
                            if child_num >= 9:
                                return request_failed(3, "部门数已达到上限")
                            else:
                                new_departmentpath = DepartmentPath
                                for i in range(0, len(new_departmentpath)):
                                    if new_departmentpath[i] != '0':
                                        continue
                                    else:
                                        index = i
                                        break
                                tmp_list = list(new_departmentpath)
                                tmp_list[index] = str((1 + child_num))
                                new_departmentpath = ''.join(tmp_list)
                                new_d = Department.objects.create(parent=d2, entity=e1, 
                                                                  name=DepartmentName,
                                                                  path=new_departmentpath)
                                return_data = {
                                    "department_path" : new_departmentpath
                                }
                                if child_num == 0:
                                    d2.children = '$' + str(new_d.id)
                                    d2.save()
                                    member_list = list(User.objects.filter(department=d2).all())
                                    for member in member_list:
                                        member.department = new_d
                                        member.save()
                                else:
                                    d2.children = d2.children + '$' + str(new_d.id)
                                    d2.save()
                                return request_success(return_data)
        else:
            return request_failed(5, "session id doesn't exist")
    else:
        return BAD_METHOD
    
    
def get_next_department(req:Request, sessionId:str, DepartmentPath:str):
    print("调用了get_next_member函数")
    print(sessionId)
    print(DepartmentPath)
    if req.method == 'GET':
        sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
        if sessionRecord:
            if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
                SessionPool.objects.filter(sessionId=sessionId).delete()
                return request_failed(3, "session id expire")
            else:
                user = sessionRecord.user
                if user.system_administrator == 0:
                    return request_failed(2, "no permissions")
                else:
                    e1 = user.entity
                    if DepartmentPath == '000000000':
                        is_leaf = False
                        root_list = list(Department.objects.filter(parent=None,entity=e1).all().order_by('path'))
                        root_num = len(root_list)
                        return_data = {
                            "is_leaf": is_leaf,
                            "member": [],
                            "Department": [
                                {
                                    "DepartmentName": root_list[i].name,
                                    "DepartmentPath": root_list[i].path,
                                    "DepartmentId": (i + 1)
                                }
                                for i in range(0, root_num)
                            ]
                        }
                        return request_success(return_data)
                    else:
                        d1 = Department.objects.filter(path=DepartmentPath,entity=e1).first()
                        if not d1:
                            return request_failed(1, "部门不存在")
                        else:
                            children_list = parse_children(d1.children)
                            child_num = len(children_list)
                            if child_num == 0:
                                is_leaf = True
                                member_list = list(User.objects.filter(department = d1).all())
                                return_data = {
                                    "is_leaf": is_leaf,
                                    "member":[
                                        return_field(member.serialize(),["Name","Department","Authority","lock"])
                                    for member in member_list 
                                    if member.super_administrator == 0 and member.system_administrator == 0],
                                    "Department": []
                                }
                                return request_success(return_data)
                            else:
                                is_leaf = False
                                child_list = list(Department.objects.filter(parent=d1,entity=e1).all().order_by('path'))
                                return_data = {
                                    "is_leaf": is_leaf,
                                    "member": [],
                                    "Department": [
                                        {
                                            "DepartmentName": child_list[i].name,
                                            "DepartmentPath": child_list[i].path,
                                            "DepartmentId": (i + 1)
                                        }
                                        for i in range(0, child_num)
                                    ]
                                }
                                return request_success(return_data)
        else:
            return request_failed(3, "session id doesn't exist")
    else:
        return BAD_METHOD

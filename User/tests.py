from django.test import TestCase
from User.models import *
from django.test import Client as DefaultClient
from User.views import *
import json
from utils.utils_other import *


class Client(DefaultClient):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def _add_cookie(self, kw):
        if "SessionID" in self.cookies:
            if "data" not in kw:
                kw["data"] = {}
            kw["data"]["SessionID"] = self.cookies["SessionID"].value
        return kw

    def post(self, *args, **kw):
        return super(Client, self).post(*args, **self._add_cookie(kw))

    def get(self, *args, **kw):
        return super(Client, self).get(*args, **self._add_cookie(kw))


class UserTests(TestCase):
    def setUp(self):
        self.raw_password = "yiqunchusheng"
        self.e1 = Entity.objects.create(name = 'CS_Company1')
        self.d1 = Department.objects.create(name = 'CS_Department1', entity = self.e1, path = '100000000')
        self.d1_1 = Department.objects.create(name = 'CS_Department1_1', entity = self.e1, parent = self.d1, path = '110000000')
        self.d1.children = '$' + str(self.d1_1.id)
        self.d1.save()
        self.u1 = User.objects.create(
            name = 'chusheng_1',password = sha256(self.raw_password),
            super_administrator = 1,system_administrator = 0, asset_administrator = 0,
            function_string = "0000000000000000000011"
        )
        self.u2 = User.objects.create(
            name="chusheng_2", password=sha256(self.raw_password),
            entity = self.e1,
            super_administrator = 0,system_administrator = 1, asset_administrator = 0,
            function_string = "0000000000000011111100"
        )
        self.u3 = User.objects.create(
            name="chusheng_3", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1_1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 1,
            function_string = "0000011111111100000000"
        )
        self.u4 = User.objects.create(
            name="chusheng_4", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1_1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 0,
            function_string = "1111100000000000000000"
        )
        self.u5 = User.objects.create(
            name="chusheng_5", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1_1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 0,
            function_string = "1111100000000000000000"
        )

# 登录测试   
    # 用户名不存在 
    def test_login1(self):
        c = Client()
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name +'hahaha', "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 2)

    # 密码不对
    def test_login2(self):
        c = Client()
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password + 'hahaha', "SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 3)

    # 成功登录 
    def test_login3(self):
        c = Client()
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
    
    # 用户已登录
    def test_login4(self):
        c = Client()
        resp1 = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp1.json()["code"], 0)
        resp2 = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        self.assertEqual(resp2.json()["code"], 0)
        resp = c.post(
            "/User/logout",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

# 登出测试 
    # 成功登出
    def test_logout1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/logout",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
    
    # sessionid不存在
    def test_logout2(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/logout",
            data={"SessionID": "0"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

    # 未登录
    def test_logout3(self):
        c = Client()
        resp = c.post(
            "/User/logout",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

# 获取用户权限测试
    # 超级管理员
    def test_userinfo1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/info/1",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["Authority"],0)

    # 系统管理员
    def test_userinfo2(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/info/2",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["Authority"],1)

    # 资产管理员
    def test_userinfo3(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "3"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/info/3",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["Authority"],2)

    # 普通用户
    def test_userinfo4(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u4.name, "Password": self.raw_password, "SessionID": "4"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/info/4",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["Authority"],3)

    # sessionid不存在
    def test_userinfo5(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/info/0",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],1)
    
    # sessionid过期    
    def test_userinfo6(self):
        SessionPool.objects.create(sessionId = "5", user = self.u5,
                                   expireAt = dt.datetime.now(pytz.timezone(TIME_ZONE)) - dt.timedelta(days=2))
        c = Client()
        resp = c.get(
            "/User/info/5",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],2)

# 查询业务实体下的所有员工测试（不算系统管理员本身）
    # 成功查询所有信息
    def test_getallmember1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/member/2",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)

    # 无权限  
    def test_getallmember2(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "3"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/member/3",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],1)

    # sessionid不存在
    def test_getallmember3(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.get(
            "/User/member/20",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],2)

    # sessionid过期    
    def test_getallmember4(self):
        SessionPool.objects.create(sessionId = "02", user = self.u2,
                                   expireAt = dt.datetime.now(pytz.timezone(TIME_ZONE)) - dt.timedelta(days=2))
        c = Client()
        resp = c.get(
            "/User/member/02",
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],2)

# 系统管理员增加部门测试
    # 无权限  
    def test_getallmember1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "3"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "3", "DepartmentPath":"000000000", "DepartmentName":"CS_Department000"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],4)

    # sessionid不存在
    def test_getallmember2(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "20", "DepartmentPath":"000000000", "DepartmentName":"CS_Department000"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],5)

    # sessionid过期    
    def test_getallmember3(self):
        SessionPool.objects.create(sessionId = "02", user = self.u2,
                                   expireAt = dt.datetime.now(pytz.timezone(TIME_ZONE)) - dt.timedelta(days=2))
        c = Client()
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "02", "DepartmentPath":"000000000", "DepartmentName":"CS_Department000"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],5)

    # DepartmentName已存在
    def test_adddepartment4(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "2", "DepartmentPath":"000000000", "DepartmentName":"CS_Department1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],1)
    
    # DepartmentPath无效
    def test_adddepartment5(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "2", "DepartmentPath":"880000000", "DepartmentName":"CS_Department2"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],2)

    # 子部门数量达到上限
    def test_adddepartment6(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        for i in range(2,10):
            resp_i = c.post(
                "/User/department/add",
                data={"SessionID": "2", "DepartmentPath":"100000000", "DepartmentName":"CS_Department1_" + str(i)},
                content_type="application/json",
            )
            self.assertEqual(resp_i.json()["code"],0)
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "2", "DepartmentPath":"100000000", "DepartmentName":"CS_Department1_10"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],3)

    # 成功创建非叶子部门的子部门
    def test_adddepartment7(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "2", "DepartmentPath":"000000000", "DepartmentName":"CS_Department2"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["department_path"],"200000000")

    # 成功创建叶子部门的子部门（把所有员工转移）
    def test_adddepartment8(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/department/add",
            data={"SessionID": "2", "DepartmentPath":"110000000", "DepartmentName":"CS_Department1_1_1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"],0)
        self.assertEqual(resp.json()["department_path"],"111000000")
    

 

        
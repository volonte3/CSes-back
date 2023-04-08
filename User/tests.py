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
        self.e1 = Entity.objects.create(name = 'CS_Company')
        self.d1 = Department.objects.create(name = 'depart1',entity = self.e1)
        self.u1 = User.objects.create(
            name = 'chusheng_1',password = sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 1,system_administrator = 0, asset_administrator = 0,
            function_string = "0000000000000000000011"
        )
        self.u2 = User.objects.create(
            name="chusheng_2", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 1, asset_administrator = 0,
            function_string = "0000000000000011111100"
        )
        self.u3 = User.objects.create(
            name="chusheng_3", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 1,
            function_string = "0000011111111100000000"
        )
        self.u4 = User.objects.create(
            name="chusheng_4", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 0,
            function_string = "1111100000000000000000"
        )
        self.u5 = User.objects.create(
            name="chusheng_5", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 0, asset_administrator = 0,
            function_string = "1111100000000000000000"
        )
        
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
        print(SessionPool.objects.filter(user=self.u1).all())
        resp = c.post(
            "/User/logout",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 1)

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

        
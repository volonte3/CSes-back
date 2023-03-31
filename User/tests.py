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
            super_administrator = 0,system_administrator = 1, asset_administrator=0
        )
        self.u2 = User.objects.create(
            name="chusheng_2", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 1,system_administrator = 0, asset_administrator=0
        )
        self.u3 = User.objects.create(
            name="chusheng_3", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 0, asset_administrator=0
        )
        SessionPool.objects.create(user = self.u1)
    
    def test_login1(self):
        c = Client()
        # c.cookies["SessionID"] = "0"
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name +'hahaha', "Password": self.raw_password, "SessionID": "0"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 2)

    def test_login2(self):
        c = Client()
        # c.cookies["SessionID"] = "0"
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password + 'hahaha', "SessionID": "0"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 3)
        
    def test_login3(self):
        c = Client()
        # c.cookies["SessionID"] = "0"
        resp = c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "0"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
    
    def test_logout(self):
        c = Client()
        # c.cookies["SessionID"] = "0"
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.u1.password, "SessionID": "0"},
            content_type="application/json",
        )
        resp = c.post(
            "/User/logout",
            data={"SessionID": "0"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)
        
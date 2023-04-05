from django.test import TestCase
from User.models import Entity,Department, User, SessionPool
from Asset.models import AssetClass, Asset, PendingRequests
from django.test import Client as DefaultClient
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



class AssetTests(TestCase):
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
            super_administrator = 0,system_administrator = 0, asset_administrator=1
        )
        self.u4 = User.objects.create(
            name="chusheng_4", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 0, asset_administrator=0
        )
        # 下面这句话应该没有作用吧
        # SessionPool.objects.create(user = self.u1)
        
        # 创建资产分类asset class简称ac
        self.ac0 = AssetClass.objects.create(
            department = self.d1, name = "department1根节点", children = "$2$3",  property = 0
        )
        self.ac1 = AssetClass.objects.create(
            department = self.d1, name = "房屋与构筑物", parent = self.ac0, children = "$4$5", property = 1
        )
        self.ac2 = AssetClass.objects.create(
            department = self.d1, name = "设备", parent = self.ac0, children = "$6$7", property = 1
        )
        self.ac3 = AssetClass.objects.create(
            department = self.d1, name = "房屋", parent = self.ac1, children = "", property = 2
        )
        self.ac4 = AssetClass.objects.create(
            department = self.d1, name = "土地", parent = self.ac1, children = "", property = 2
        )
        self.ac5 = AssetClass.objects.create(
            department = self.d1, name = "信息化设备", parent = self.ac2, children = "", property = 2
        )
        self.ac6 = AssetClass.objects.create(
            department = self.d1, name = "车辆", parent = self.ac2, children = "", property = 2
        )
        
    def test_tree1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.post(
            "/Asset/tree",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        print("-------------")
        print(resp.json()["treeData"])
        print("-------------")
        self.assertEqual(resp.json()["code"], 0)
# Create your tests here.

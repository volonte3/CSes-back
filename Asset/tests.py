from django.test import TestCase
from User.models import Entity,Department, User, SessionPool
from Asset.models import AssetClass, Asset, PendingRequests
from django.test import Client as DefaultClient
from utils.utils_other import *
from utils.utils_asset import *

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
            super_administrator = 1,system_administrator = 0, asset_administrator=0
        )
        self.u2 = User.objects.create(
            name="chusheng_2", password=sha256(self.raw_password),
            entity = self.e1,department= self.d1,
            super_administrator = 0,system_administrator = 1, asset_administrator=0
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
            department = self.d1, name = "department1 资产分类树", children = "$2$3",  property = 0
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
        
    def test_tree_1(self):
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )
        resp = c.post(
            "/Asset/tree",
            data={"SessionID": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.json()["code"], 0)

    def test_superuser_create_1(self):
        # 检查正常返回
        c = Client()
        
        # 先进行登录
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 然后进行创建
        resp = c.put(
            "/SuperUser/Create",
            data={"SessionID": "1", "UserName": "张三", "EntityName":"大象金融"},
            content_type="application/json",
        )

        # 用创建的这个系统管理员登录一下
        resp2 = c.post(
            "/User/login",
            data={"UserName": "张三", "Password": MD5("yiqunchusheng"), "SessionID": "3"},
            content_type="application/json",
        )

        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(resp2.json()["code"], 0 )

    def test_superuser_create_2(self):
        # 检查非超级管理员登录
        # 返回:request_failed(3, "非超级管理员，没有对应权限")
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u2.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )

        # 然后再根据登录的sessionID进行功能实现
        resp = c.put(
            "/SuperUser/Create",
            data={"SessionID": "2", "UserName": "张三", "EntityName":"大象金融"},
            content_type="application/json",
        )
        

        self.assertEqual(resp.json()["code"], 3)
    
    def test_superuser_create_3(self):
        # 检查创建同名
        # 返回:request_failed(4, "存在重复用户名")
        c = Client()
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "2"},
            content_type="application/json",
        )

        # 然后再根据登录的sessionID进行
        resp = c.put(
            "/SuperUser/Create",
            data={"SessionID": "2", "UserName": "chusheng_1", "EntityName":"大象金融"},
            content_type="application/json",
        )
        

        self.assertEqual(resp.json()["code"], 4)
    
    def test_superuser_delete_1(self):
        c = Client()

        # 超级管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 然后进行创建
        resp1 = c.put(
            "/SuperUser/Create",
            data={"SessionID": "1", "UserName": "张三", "EntityName":"大象金融"},
            content_type="application/json",
        )

        # 超级管理员发送delete请求
        resp2 = c.delete(
            "/SuperUser/Delete/1/大象金融", 
            content_type="application/json",
        )

        self.assertEqual(resp2.json()["code"], 0)
    
    def test_superuser_delete_2(self):
        c = Client()

        # 超级管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 然后进行创建
        resp1 = c.put(
            "/SuperUser/Create",
            data={"SessionID": "1", "UserName": "张三", "EntityName":"大象金融"},
            content_type="application/json",
        )

        # 超级管理员发送delete请求
        resp2 = c.delete(
            "/SuperUser/Delete/1/大象金融", 
            content_type="application/json",
        )

        # 然后试图登录张三这个账号
        # 用创建的这个系统管理员登录一下
        resp3 = c.post(
            "/User/login",
            data={"UserName": "张三", "Password": MD5("yiqunchusheng"), "SessionID": "3"},
            content_type="application/json",
        )

        self.assertEqual(resp2.json()["code"], 0)
        self.assertEqual(resp3.json()["code"], 2)
    
    def test_superuser_info_1(self):

        c = Client()

        # 超级管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u1.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

         # 然后进行创建
        resp1 = c.put(
            "/SuperUser/Create",
            data={"SessionID": "1", "UserName": "张三", "EntityName":"大象金融"},
            content_type="application/json",
        )

        # 然后获取信息
        resp = c.get(
            "/SuperUser/info/1",
            content_type="application/json",
        )

        debug_print("返回体", resp.json())

        self.assertEqual(resp.json()["code"], 0)
    
    def test_add_asset_class_1(self):
        c = Client()

        # 资产管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # parent_asset_class = get_asset_class(1)
        # debug_print("former children", parent_asset_class.children)

        # 资产管理员调用add_asset_class函数
        resp = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 1, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        # parent_asset_class = get_asset_class(1)
        # debug_print("later children", parent_asset_class.children)

        self.assertEqual(resp.json()["code"], 0)
    
    def test_add_asset_class_2(self):
        # 测试能否创建同名资产分类
        c = Client()

        # 资产管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )


        # 资产管理员调用add_asset_class函数
        resp = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 1, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        # 再调用一次
        resp2 = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 0, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )


        self.assertEqual(resp.json()["code"], 0)
        self.assertEqual(resp2.json()["code"], 4)
    
    def test_modify_asset_class_1(self):
        c = Client()

        # 资产管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 资产管理员调用add_asset_class函数
        resp = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 1, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        asset_class = get_asset_class(1)
        debug_print(asset_class.property, asset_class.name)

        # 资产管理员调用modify_asset_class函数
        resp2 = c.post(
            "/Asset/ModifyAssetClass",
            data={"SessionID": "1", "NodeValue": 1, "AssetClassName": "改成这一个资产类别", "NaturalClass": 2},
            content_type="application/json",
        )

        self.assertEqual(resp2.json()["code"], 5)

    def test_modify_asset_class_2(self):
        c = Client()

        # 资产管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 资产管理员调用add_asset_class函数
        resp = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 1, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        asset_class = get_asset_class(1)
        debug_print(asset_class.property, asset_class.name)

        # 资产管理员调用modify_asset_class函数
        resp2 = c.post(
            "/Asset/ModifyAssetClass",
            data={"SessionID": "1", "NodeValue": 1, "AssetClassName": "改成这一个资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        asset_class = get_asset_class(1)
        debug_print(asset_class.property, asset_class.name)

        self.assertEqual(resp2.json()["code"], 0)
    
    def test_delete_asset_class(self):
        c = Client()

        # 资产管理员先登录
        c.post(
            "/User/login",
            data={"UserName": self.u3.name, "Password": self.raw_password, "SessionID": "1"},
            content_type="application/json",
        )

        # 资产管理员调用add_asset_class函数
        resp = c.post(
            "/Asset/AddAssetClass",
            data={"SessionID": "1", "ParentNodeValue": 1, "AssetClassName": "这是一个待添加的资产类别", "NaturalClass": 0},
            content_type="application/json",
        )

        root_node = AssetClass.objects.filter(id=1).first()
        debug_print("root_node", root_node.children)
        all_node = AssetClass.objects.all()
        debug_print("all", len(all_node))


        # 资产管理员调用delete_asset_class函数
        resp2 = c.delete(
            "/Asset/DeleteAssetClass/1/8",
            content_type="application/json",
        )

        resp3 = c.delete(
            "/Asset/DeleteAssetClass/1/2",
            content_type="application/json",
        )

        root_node = AssetClass.objects.filter(id=1).first()
        debug_print("root_node", root_node.children)
        all_node = AssetClass.objects.all()
        debug_print("all", len(all_node))



        self.assertEqual(resp2.json()["code"], 0)
        self.assertEqual(resp3.json()["code"], 0)











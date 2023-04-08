from Asset.models import *
from User.models import *
from utils.utils_other import *

def add_asset_class_1():
    d1 = Department.objects.filter(id = 1).first()
    ac0 = AssetClass.objects.create(
        department = d1, name = d1.name + " 资产分类树", children = "$2$3",  property = 0
    )
    ac1 = AssetClass.objects.create(
        department = d1, name = "房屋与构筑物", parent = ac0, children = "$4$5", property = 1
    )
    ac2 = AssetClass.objects.create(
        department = d1, name = "设备", parent = ac0, children = "$6$7", property = 1
    )
    ac3 = AssetClass.objects.create(
        department = d1, name = "房屋", parent = ac1, children = "", property = 2
    )
    ac4 = AssetClass.objects.create(
        department = d1, name = "土地", parent = ac1, children = "", property = 2
    )
    ac5 = AssetClass.objects.create(
        department = d1, name = "信息化设备", parent = ac2, children = "", property = 2
    )
    ac6 = AssetClass.objects.create(
        department = d1, name = "车辆", parent = ac2, children = "", property = 2
    )

def delete_user_class_1():
    User.objects.all().delete()
    SessionPool.objects.all().delete()

def add_user_class_1():
    raw_password = "yiqunchusheng"
    e1 = Entity.objects.create(name = 'CS_Company')
    d1 = Department.objects.create(name = 'depart1',entity = e1)
    u1 = User.objects.create(
        name = 'chusheng_1',password=sha256(MD5((raw_password))),
        entity = e1,department= d1,
        super_administrator = 1,system_administrator = 0, asset_administrator = 0,
        function_string = "0000000000000000000011"
    )
    u2 = User.objects.create(
        name="chusheng_2", password=sha256(MD5((raw_password))),
        entity = e1,department= d1,
        super_administrator = 0,system_administrator = 1, asset_administrator = 0,
        function_string = "0000000000000011111100"
    )
    u3 = User.objects.create(
        name="chusheng_3", password=sha256(MD5((raw_password))),
        entity = e1,department= d1,
        super_administrator = 0,system_administrator = 0, asset_administrator = 1,
        function_string = "0000011111111100000000"
    )
    u4 = User.objects.create(
        name="chusheng_4", password=sha256(MD5((raw_password))),
        entity = e1,department= d1,
        super_administrator = 0,system_administrator = 0, asset_administrator = 0,
        function_string = "1111100000000000000000"
    )
    u5 = User.objects.create(
        name="chusheng_5", password=sha256(MD5((raw_password))),
        entity = e1,department= d1,
        super_administrator = 0,system_administrator = 0, asset_administrator = 0,
        function_string = "1111100000000000000000"
    )
from Asset.models import AssetClass
from User.models import Department


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
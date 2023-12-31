from django.db import models
from User.models import User, Entity, Department
# Create your models here.

# 本表用于记录资产类别 ( 自己添加 )
class AssetClass(models.Model):
    id = models.BigAutoField(primary_key = True)  # 资产类别的 id 
    department = models.ForeignKey(to = Department, on_delete = models.CASCADE)
    name = models.CharField(max_length = 128)     # 资产类别, 如"房地产"
    parent = models.ForeignKey(to = "AssetClass", on_delete = models.CASCADE, null = True)
    children = models.CharField(max_length=256, null = True)   # 存储方式, $1$2....
    property = models.IntegerField()  # 资产类别属性 
    # 0: 根节点
    # 1: 非根节点, 非品类
    # 2: 尚未被定义为条目型资产还是数量型资产的品类
    # 3: 条目型资产品类
    # 4: 数量型资产品类
    
    def __str__(self):
        return self.name

# 本表用于记录资产有关的信息
class Asset(models.Model):
    id = models.BigAutoField(primary_key = True)
    parent = models.ForeignKey(to = "Asset", on_delete = models.CASCADE, null = True) # 上一级 Asset
    name = models.CharField(max_length = 128)
    Class = models.ForeignKey(to = AssetClass, on_delete = models.CASCADE)  # 注意, Class 字段为了区别关键字 class, 首字母大写
    user = models.ForeignKey(to = User, on_delete = models.CASCADE)
    price = models.DecimalField(max_digits = 8, decimal_places = 2)
    description = models.CharField(max_length = 128)
    position = models.CharField(max_length = 128)
    expire = models.IntegerField()

    def __str__(self):
        return self.name

class PendingRequests(models.Model):
    id = models.BigAutoField(primary_key = True)
    initiator = models.ForeignKey(to = User, on_delete = models.CASCADE, related_name = 'PendingRequests_initiator')
    participant = models.ForeignKey(to = User, on_delete = models.CASCADE, null = True, related_name = 'PendingRequests_participant')
    asset = models.ForeignKey(to = Asset, on_delete = models.CASCADE)
    type = models.IntegerField()
    result = models.IntegerField()
    request_time = models.IntegerField()
    review_time = models.IntegerField()

    def __str__(self):
        return self.id

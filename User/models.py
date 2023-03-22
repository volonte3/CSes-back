
from django.db import models

# 本条用于记录业务实体的信息
class Entity(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 128)

    def __str__(self):
        return self.name

# 本表用于记录组织有关的信息
class Department(models.Model):
    id = models.BigAutoField(primary_key = True)
    parent = models.ForeignKey(to = "Department", on_delete = models.CASCADE, null = True) # 上一级 Department
    entity = models.ForeignKey(to = Entity, on_delete = models.CASCADE)
    name = models.CharField(max_length = 128)

    def __str__(self):
        return self.name

# 本表用于记录用户的信息
class User(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 128, unique = True)
    password = models.CharField(max_length = 32)
    entity = models.ForeignKey(to = Entity, on_delete = models.CASCADE)
    department = models.ForeignKey(to = Department, on_delete = models.CASCADE)
    entity_super = models.IntegerField()   # 用户是否为业务实体的系统管理员
    system_super = models.IntegerField()   # 用户是否为系统的超级管理员

    def __str__(self):
        return self.name

# 本表用于记录资产类别 ( 自己添加 )
class AssetClass(models.Model):
    id = models.BigAutoField(primary_key = True)  # 资产类别的 id 
    name = models.CharField(max_length = 128)     # 资产类别, 如"房地产"
    
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






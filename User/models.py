from django.db import models
import utils.model_date as getTime

# 本表用于记录业务实体的信息
class Entity(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 128)

    def __str__(self):
        return self.name

# 本表用于记录组织有关的信息
class Department(models.Model):
    id = models.BigAutoField(primary_key = True)
    parent = models.ForeignKey(to = "Department", on_delete = models.CASCADE, null = True) # 上一级 Department
    children = models.CharField(max_length=256, null = True)   # 存储方式, $1$2....
    entity = models.ForeignKey(to = Entity, on_delete = models.CASCADE)
    name = models.CharField(max_length = 128)
    chi

    def __str__(self):
        return self.name

# 本表用于记录用户的信息
class User(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 128, unique = True)
    password = models.CharField(max_length=100)
    entity = models.ForeignKey(to = Entity, on_delete = models.CASCADE)
    department = models.ForeignKey(to = Department, on_delete = models.CASCADE)
    super_administrator = models.IntegerField()   # 用户是否为超级管理员
    system_administrator = models.IntegerField()  # 用户是否为系统管理员
    asset_administrator = models.IntegerField()   # 用户是否为资产管理员
    function_string = models.CharField(max_length=50)          # 代表该用户的权能01字符串

    def __str__(self):
        return self.name

# honorcode: from https://github.com/c7w/ReqMan-backend/blob/dev/ums/models.py
class SessionPool(models.Model):
    sessionId = models.CharField(max_length=48) # 实际长度: 32
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(default=getTime.get_datetime) # TODO:搞清楚这里的get_datetime

    class Mata:
        indexes = [models.Index(fields=["sessionId"])]






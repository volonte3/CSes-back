from django.db import models
import utils.model_date as getTime

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

# honorcode: from https://github.com/c7w/ReqMan-backend/blob/dev/ums/models.py
class SessionPool(models.Model):
    sessionId = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(default=getTime.get_datetime)

    class Mata:
        indexes = [models.Index(fields=["sessionId"])]






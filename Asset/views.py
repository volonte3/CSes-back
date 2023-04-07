from Asset.models import AssetClass
from User.models import User, Entity
from utils.utils_request import request_success
from utils.utils_asset import * 
from utils.config import *
from rest_framework.request import Request
from django.http import HttpResponse
from utils.utils_add_data import add_asset_class_1

def add_data(req: Request):
    # add_asset_class_1()
    # ac0 = AssetClass.objects.filter(id = 1).first()
    return HttpResponse("Congratulations! You have successfully added many data. Go ahead!")

def _add_asset_class(usr:User, data):

    # TODO: 判断是否存在同名的资产分类

    AssetClass.objects.create(
        deparment = usr.department, name = data["asset_class_name"], \
        parent = get_asset_class(data["parent_node_value"]), children = "", \
        property = 1 # TODO:先暂时定成1
    )



def add_asset_class(req: Request):
    # 先解析出数据, 
    pass
    # 增加一个资产类别类



def _give_tree(usr, data=None):
    # 根据这个usr的department_id来给出这个department的资产分类树
    
    # 找到这个department的根节点
    rootNode = AssetClass.objects.filter(department = usr.department, property = 0).first()

    treeData = {}
    treeData['title'] = rootNode.name
    treeData['value'] = rootNode.id

    children = []
    # 遍历这个根节点的孩子节点
    children_list = parse_children(rootNode.children)
    for child_id in children_list:
        children.append(give_subtree_recursive(child_id, usr.department.id))
    treeData['children'] = children

    return request_success({"treeData":treeData})

def give_tree(req: Request):
    return AssetWarpper(req=req, function=_give_tree, authority_level=ONLY_ASSET_ADMIN)

def _superuser_create(usr, data):
    UserName = data["UserName"]
    EntityName = data["EntityName"]

    # 如果该用户本来就存在
    filtered_user = User.objects.filter(name=UserName).first()
    if(filtered_user != None):
        return request_failed(4, "存在重复用户名")
    
    # 如果存在重复业务实体
    filtered_entity = Entity.objects.filter(name=EntityName).first()
    if(filtered_entity != None):
        return request_failed(5, "存在重复业务实体")

    # 新建一个entity
    e = Entity.objects.create(name = EntityName)

    # TODO: 随机设置一个密码, 先使用固定密码yiqunchusheng
    raw_password = "yiqunchusheng"

    # 新建一个系统管理员
    User.objects.create(
        name = UserName ,password = sha256(MD5(raw_password)),
        entity = e ,department= None,
        super_administrator = 0,system_administrator = 1, asset_administrator=0,
        function_string = "0000000000000011111100"
    )

    return request_success()



def superuser_create(req: Request):
    return AssetWarpper(req=req, function=_superuser_create, authority_level=ONLY_SUPER_ADMIN, \
        data_require=["UserName", "EntityName"])

    

    

from Asset.models import AssetClass
from User.models import User, Entity
from utils.utils_request import request_success
from utils.utils_asset import * 
from utils.config import *
from rest_framework.request import Request
from django.http import HttpResponse
from utils.utils_add_data import add_asset_class_1

def _add_asset_class(usr:User, data):

    # 判断是否存在同名的资产分类
    same_name = AssetClass.objects.filter(name = data["AssetClassName"], department = usr.department)
    if(len(same_name) != 0):
        return request_failed(4, "该部门内存在同名资产分类")


    natural_class = data["NaturalClass"]
    if natural_class == 0:
        property = 1
    elif natural_class == 1:
        property = 4
    elif natural_class == 2:
        property = 3
    else:
        raise KeyError

    parent_asset_class = get_asset_class(data["ParentNodeValue"])
    asset_class = AssetClass.objects.create(
        department = usr.department, name = data["AssetClassName"], \
        parent = parent_asset_class, children = "", \
        property = property
    )

    # 修改父亲节点的children
    parent_asset_class.children += ('$' + str(asset_class.id))
    parent_asset_class.save()
    
    return request_success()

def _modify_asset_class(usr: User, data):

    # 判断是否存在同名的资产分类
    same_name = AssetClass.objects.filter(name = data["AssetClassName"], department = usr.department)
    if(len(same_name) != 0 and same_name.id != data["NodeValue"]):
        return request_failed(4, "该部门内存在同名资产分类")
    
    natural_class = data["NaturalClass"]
    if natural_class == 0:
        property = 1
    elif natural_class == 1:
        property = 4
    elif natural_class == 2:
        property = 3
    else:
        raise KeyError

    asset_class = AssetClass.objects.filter(id=data["NodeValue"]).first()
    if (asset_class.property == 0) and data["NaturalClass"] != 0:
        return request_failed(5, "不能修改根节点的自然分类")
    
    # 进行更改
    asset_class.name = data["AssetClassName"]
    if (asset_class.property != 0):
        asset_class.property = property
    asset_class.save()

    return request_success()

def modify_asset_class(req: Request):
    return AssetWarpper(req=req, function=_modify_asset_class, authority_level=ONLY_ASSET_ADMIN, \
        data_require=["AssetClassName", "NodeValue", "NaturalClass"])

def _delete_asset_class(user: User, data):
    debug_print("NodeValue", data["NodeValue"])

    # 检查该节点是否存在
    to_delete = AssetClass.objects.filter(id = data["NodeValue"], department = user.department).first()
    if(to_delete == None):
        return request_failed(4, "该节点不存在")
    
    # 检查该节点是否为根节点
    if (to_delete.property == 0):
        return request_failed(5, "该节点为根节点，不能删除")

    # 之后递归删数据, 因为之后可能还需要检查同名, 所以要把数据真正地删掉
    subtree_list = []
    subtree_list = give_subtree_list_recursive(asset_class_id=data["NodeValue"], department_id=user.department.id, subtree_list=subtree_list)
    debug_print("subtree_list", subtree_list)

    # 修改父节点的children:
    parent_node = AssetClass.objects.filter(id = to_delete.parent.id).first()
    new_children_string = delete_child(parent_node.children, data["NodeValue"])
    parent_node.children = new_children_string
    parent_node.save()


    # 删除 subtree_list 中的资产分类
    for sub_node in subtree_list:
        AssetClass.objects.filter(id = sub_node).delete()
    
    return request_success()


def delete_asset_class(req: Request, SessionID:str, NodeValue: int):
    data_pass = {}
    data_pass["session_id"] = SessionID
    data_pass["NodeValue"] = NodeValue
    return AssetWarpper(req=req, function=_delete_asset_class, authority_level=ONLY_ASSET_ADMIN, \
        data_pass=data_pass)
    

def add_asset_class(req: Request):

    return AssetWarpper(req=req, function=_add_asset_class, authority_level=ONLY_ASSET_ADMIN, \
        data_require=["AssetClassName", "ParentNodeValue", "NaturalClass"])



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

    return request_success({"treeData":[treeData]})

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


def _superuser_delete(usr, data):
    entity_name = data["entity_name"]

    # 找到该实体进行删除
    filtered_entity = Entity.objects.filter(name=entity_name).first()
    if(filtered_entity == None):
        return request_failed(4, "实体不存在")
    Entity.objects.filter(name=entity_name).delete()
    # 所有与该实体关联的用户应该也都级联删除了
    return request_success()  

def superuser_delete(req: Request, SessionID: str, EntityName: str):
    data_pass = {}
    data_pass["session_id"] = SessionID
    data_pass["entity_name"] = EntityName
    return AssetWarpper(req=req, function=_superuser_delete, authority_level=ONLY_SUPER_ADMIN, data_pass=data_pass)

def _superuser_info(usr, data=None):

    # 把所有的业务实体和对应的系统管理员都返回

    # 筛选出所有系统管理员
    system_user_list = User.objects.filter(system_administrator=1)
    entity_manager = []
    for system_user in system_user_list:
        item = {}
        # item[system_user.entity.name] = system_user.name
        item["Entity"] = system_user.entity.name
        item["Manager"] = system_user.name
        entity_manager.append(item)
    return_data = {}
    return_data["entity_manager"] = entity_manager
    return request_success(return_data)

def superuser_info(req: Request, SessionID: str):
    data_pass = {}
    data_pass["session_id"] = SessionID
    return AssetWarpper(req=req, function=_superuser_info, authority_level=ONLY_SUPER_ADMIN, data_pass=data_pass)
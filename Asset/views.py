from Asset.models import AssetClass
from User.models import User
from utils.utils_request import request_success
from utils.utils_asset import * 
from utils.config import *

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
    treeData = []

    # 找到这个department的根节点
    rootNode = AssetClass.objects.filter(department = usr.department, property = 0).first()
    # 遍历这个根节点的孩子节点
    children_list = parse_children(rootNode.children)
    for child_id in children_list:
        treeData.append(give_subtree_recursive(child_id, usr.department.id))

    return request_success({"treeData":treeData})

def give_tree(req: Request):
    return AssetWarpper(req=req, function=_give_tree, authority_level=ONLY_ASSET_ADMIN)


    


    

    

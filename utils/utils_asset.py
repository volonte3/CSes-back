from Asset.models import AssetClass, Asset

# 可以多写一个鉴定用户是不是资产管理、有没有权限修改的函数

def get_asset(asset_class_id):
    asset_class = AssetClass.objects.filter(id=asset_class_id).first()
    assert(asset_class != None, "Asset Class NOT Found!")
    return asset_class

def parse_children(children_string):
    # 这里要不要增加children_string==None的一个判断
    children_list = children_string.split('$')
    return children_list[1:]  # 去除最前面的一个空格

def give_subtree_recursive(asset_class_id):
    nodeData = {}

    # 把这个asset_class的title与value填写到nodeData中, value直接写asset_class_id
    asset_class = get_asset(asset_class_id)
    nodeData['title'] = asset_class.name
    nodeData['value'] = asset_class_id

    # 解析出children_list
    children_list = parse_children(asset_class.children)

    # 如果这个asset_class没有children, 直接返回nodeData
    # if(children_list)

    # 如果这个asset_class有children
    children = []
    for child_id in children_list:
        children.append(give_subtree_recursive(child_id))

    nodeData["children"] = children

    return nodeData

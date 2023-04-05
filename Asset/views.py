from models import Asset, AssetClass

def add_asset_class():
    pass
    # 增加一个资产类别类









    

def give_tree(deparment_id):
    # 给前端返回一个树, 采用json套json的格式, 参考https://ant.design/components/tree-select-cn格式
    # 格式样例：
    # const treeData = [
    #     {
    #         title: 'Node1',
    #         value: '0-0',
    #         children: [
    #         {
    #             title: 'Child Node1',
    #             value: '0-0-1',
    #         },
    #         {
    #             title: 'Child Node2',
    #             value: '0-0-2',
    #         },
    #         ],
    #     },
    #     {
    #         title: 'Node2',
    #         value: '0-1',
    #     },
    # ];
    
    # 先从数据库中选出该deperment_id的根节点root

    treeData = []

    

from Asset.models import Asset, AssetClass
from User.models import SessionPool
from rest_framework.request import Request
from utils.sessions import get_session_id
from utils.utils_other import *
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
import pytz
import datetime as dt
from CS_Company_backend.settings import TIME_ZONE

def add_asset_class():
    pass
    # 增加一个资产类别类









    

def give_tree(req: Request):

    # TODO: 检验这个Request请求的正确性,下面先写正确的一支

    if req.method == 'POST':
        session_id = get_session_id(req)
    
    # 下面是 session_id to user的过程
    sessionRecord =SessionPool.objects.filter(sessionId=session_id).first()
    if sessionRecord:
        if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
            SessionPool.objects.filter(sessionId=session_id).delete()
            return request_failed(2, "session id expire")
        else:
            usr = sessionRecord.user
            
            return request_success({"data":usr.name})
    else:
        return request_failed(1, "session id doesn't exist")




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

    

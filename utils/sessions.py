# honorcode: https://github.com/c7w/ReqMan-backend/blob/dev/utils/sessions.py
from User.models import SessionPool, User


def get_session_id(request):
    if request.method == "POST":
        return request.data.get("sessionId")

def bind_session_id(sessionId: str, user: User):
    # 将一个sessionId与一个用户进行绑定
    SessionPool.objects.create(sessionId=sessionId, user=user)
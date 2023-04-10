from django.urls import path, include
import User.views as views

urlpatterns = [
    # 本地测试时增加/删除数据
    path('/add_data', views.add_data), 
    path('/delete_data', views.delete_data), 
    # 用于用户登录登出
    path('/login', views.login),
    path('/logout', views.logout),
    path('/info/<str:sessionId>',views.user_info),
    # 用于系统管理员维护部门和员工
    path('/member/<str:sessionId>',views.get_all_member),
    path('/add',views.add_member),
    path('/remove/<str:sessionId>/<str:UserName>',views.remove_member),
    path('/lock',views.lock_member),
    path('/ChangeAuthority',views.change_authority),

    path('/department/add',views.add_department),
    path('/department/<str:sessionId>/<str:DepartmentPath>',views.get_next_department),
]

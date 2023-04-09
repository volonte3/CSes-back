from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/login', views.login),
    path('/logout', views.logout),
    path('/add_data', views.add_data), 
    path('/delete_data', views.delete_data), 
    path('/info/<str:sessionId>',views.user_info),
    path('/add',views.add_member),
    path('/remove/<str:sessionId>/<str:UserName>',views.remove_member),
    path('/member/<str:sessionId>',views.get_all_member),
    path('/department/add',views.add_department),
    path('/department/<str:sessionId>/<str:DepartmentPath>',views.get_next_department),
]

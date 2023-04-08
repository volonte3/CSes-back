from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/login', views.login),
    path('/logout', views.logout),
    path('/add_data', views.add_data), 
    path('/delete_data', views.delete_data), 
    path('/info/<str:sessionId>',views.user_info),
    path('/member/<str:sessionId>',views.get_all_member),
]

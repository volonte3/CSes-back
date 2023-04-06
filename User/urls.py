from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/login', views.login),
    path('/logout', views.logout),
    path('/info/<str:sessionId>',views.user_info, name="user_info"),
    # path('/member/<str:sessionId>',views.get_all_member)
]

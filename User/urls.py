from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/startup', views.startup),
    path('/login', views.login)
]

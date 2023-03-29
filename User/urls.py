from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/login', views.login),
    path('/logout', views.logout)
]

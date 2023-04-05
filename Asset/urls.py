from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('/tree', views.give_tree), 
]

from django.urls import path, include
import Asset.views as views

urlpatterns = [
    path('/tree', views.give_tree), 
    # path('/add_data', views.add_data), 
    path('/Create', views.superuser_create),
    path('/Delete/<str:SessionID>/<str:EntityName>', views.superuser_delete, name="superuser_delete"),
    path('/info/<str:SessionID>', views.superuser_info),
    path('/AddAssetClass', views.add_asset_class),
    path('/ModifyAssetClass', views.modify_asset_class),
    path('/DeleteAssetClass/<str:SessionID>/<int:NodeValue>', views.delete_asset_class)
]

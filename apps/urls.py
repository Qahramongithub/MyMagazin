from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

from apps.views.branch import BulkTransferAPIView, BranchListApiView
from apps.views.company import CompanyStatusAPIView
from apps.views.warehouse import (
    WarehouseCreateApiView,
    WarehouseListApiView,
    WarehouseDetailApiView, WarehouseDeleteApiView, WarehouseStartApiView, WarehouseEndApiView
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

]

urlpatterns += [
    # path('api/warehouse/create', WarehouseCreateApiView.as_view(), name='warehouse_create'),
    path('api/warehouse/list', WarehouseListApiView.as_view(), name='warehouse_list'),
    # path('api/warehouse/detail/<int:pk>/', WarehouseDetailApiView.as_view(), name='warehouse_detail'),
    # path('api/warehouse/delete/<int:pk>/', WarehouseDeleteApiView.as_view(), name='warehouse_delete'),
    # path('api/warehouse/user/list', WarehouseListApiView.as_view(), name='warehouse_list'),
]
urlpatterns += [
    path('api/warehouse/start', WarehouseStartApiView.as_view(), name='warehouse_start'),
    path('api/warehouse/stop/<int:pk>', WarehouseEndApiView.as_view(), name='warehouse_stop'),
]

urlpatterns += [
    path('api/company/status', CompanyStatusAPIView.as_view(), name='company_status'),
]
urlpatterns += [
    path('warehouse/transfer', BulkTransferAPIView.as_view(), name='warehouse_transfer'),
    # path('warehouse/list', BranchListApiView.as_view(), name='warehouse_list'),
]

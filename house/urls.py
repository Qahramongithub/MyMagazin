from django.urls import path

from house.views.analitica import DailySaleListView, MonthlySaleListView, AnaliticaListView
from house.views.category import CategoryCreateApiView, CategoryListApiView, CategoryDeleteApiView, \
    CategoryUpdateApiView
from house.views.exel import ProductExcelExportView
from house.views.order import OrderListCreateAPIView
from house.views.product import ProductCreateApiView, ProductListApiView, FinishedProductListApiView, \
    LowProductListApiView, ProductUpdateApiView, ProductDeleteApiView

urlpatterns = [
    path('category/create', CategoryCreateApiView.as_view()),
    path('category/list', CategoryListApiView.as_view()),
    path('category/delete/<int:pk>', CategoryDeleteApiView.as_view()),
    path('category/update/<int:pk>', CategoryUpdateApiView.as_view()),
]

# ====================     Product ================================
urlpatterns += [
    path('product/create', ProductCreateApiView.as_view()),
    path('product/delete/<int:pk>', ProductDeleteApiView.as_view()),
    path('product/update/<int:pk>', ProductUpdateApiView.as_view()),
    path('product/list', ProductListApiView.as_view()),
    path('product/finish', FinishedProductListApiView.as_view()),
    path('product/low', LowProductListApiView.as_view()),
]

# ======================       Order ================================
urlpatterns += [
    path('order/create', OrderListCreateAPIView.as_view()),
]

urlpatterns += [
    path('daily/', DailySaleListView.as_view()),
    path('monthly', MonthlySaleListView.as_view()),
    # path('sale/', SaleListView.as_view()),
    path('analitica/', AnaliticaListView.as_view()),
    path('exel', ProductExcelExportView.as_view()),
]

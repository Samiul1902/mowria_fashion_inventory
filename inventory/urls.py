from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:pk>/adjust-size/', views.adjust_size_stock, name='adjust_size_stock'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
    path('switch-role/', views.quick_switch_demo_role, name='switch_role'),
]

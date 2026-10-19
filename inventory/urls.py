from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:pk>/adjust-size/', views.adjust_size_stock, name='adjust_size_stock'),
    path('export/csv/', views.export_inventory_csv, name='export_inventory_csv'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
    path('switch-role/', views.quick_switch_demo_role, name='switch_role'),
]

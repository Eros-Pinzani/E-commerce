from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager_categories/', views.manager_categories, name='manager_categories'),
    path('manager_products/', views.manager_products, name='manager_products'),
    path('manager_variations/', views.manager_variations, name='manager_variations'),
    path('manager_stock/', views.manager_stock, name='manager_stock'),
    path('product_edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('get_variation_types_for_product/', views.get_variation_types_for_product, name='get_variation_types_for_product'),
]
from django.contrib import admin
from django.urls import path
from assestapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.reg, name='home'),
    path('log/', views.log, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('product/', views.product, name='product'),
    path('producttable/', views.producttable, name='producttable'),
    path('logout/', views.logout_view, name='logout'),
    path('filter/', views.filter, name='filter'),
    path('toggle-status/<str:empId>/', views.toggle_user_status, name='toggle_user_status'),
    path('product/', views.product, name='product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('assigned/', views.assigned_view, name='assigned_view'),
    path('productfilter/', views.productfilter, name='productfilter'),
    path('save/', views.handle_ajax, name='handle_ajax'),
    # path('delete/', views.delete_ajax, name='delete_ajax'),
]




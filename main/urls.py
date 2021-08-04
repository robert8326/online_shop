from django.urls import path
from .views import *

urlpatterns = [
    path('test', test_view, name='test'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail')
]

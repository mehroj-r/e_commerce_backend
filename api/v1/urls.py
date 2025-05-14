from django.urls import path, include
from api.v1.views import ProductsListAPIView

urlpatterns = [
    path('products/', ProductsListAPIView.as_view()),
    path('payments/', include('payments.urls')),
]
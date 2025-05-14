from rest_framework import generics
from app.models import Product
from .serializers import ProductSerializer

class ProductsListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
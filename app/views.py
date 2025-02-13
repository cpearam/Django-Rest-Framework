from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from app.serializers import ProductSerializer, OrderSerializer
from app.models import Product, Order, OrderItem
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializers = ProductSerializer(products, many=True)
    return Response(serializers.data)

@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializers = ProductSerializer(product)
    return Response(serializers.data)

@api_view(['GET'])
def orders_list(request):
    order = Order.objects.all()
    serializers = OrderSerializer(order, many=True)
    return Response(serializers.data)
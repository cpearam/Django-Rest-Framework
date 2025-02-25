from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock',
        )
        
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "the price must be greater than 0"
            ) 
        return value
    
class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        source='product.price')
    
    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal',
        )
        
class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = (
                'product',
                'quantity'
            )
            
    items = OrderItemCreateSerializer(many=True, required=False)
    order_id = serializers.UUIDField(read_only=True)
    
    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)
        return order
    
    
    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            
            if orderitem_data is not None:
                instance.items.all().delete()
                
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)
        return instance
        
    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items'
        )
        extra_kwargs = {
            'user': {'read_only': True}
        }
    
class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)
    
    class Meta:
        model = Order
        fields = (
            'order_id',
            'created_at',
            'user',
            'status',
            'items',
            'total_price',
        )
        
from django.forms import model_to_dict
from rest_framework import serializers

from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = super().create(validated_data)
        for position in positions:
            post_stock = StockProduct.objects.create(quantity=position['quantity'],
                                                     price=position['price'],
                                                     product_id=position['product'].id,
                                                     stock_id=stock.id)
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)
        for position in positions:
            patch_stock = StockProduct.objects.update_or_create(product_id=position['product'].id,
                                                                stock_id=stock.id,
                                                                defaults={
                                                                'quantity': position['quantity'],
                                                                'price': position['price']
                                                                })
        return stock
from Product.models import Product , ProductPrice
from rest_framework import serializers
from html import unescape
from tmp.models import *
import re

class OurPharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurPharmacie
        fields = ['id', 'title', 'address', 'shift', 'phone_number', 'lat', 'lon']


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['price', 'amount', 'unique_identifier']


class ProductSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField() 
    product_type_display = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Product
        fields = ['id', 'name','info','producer','country','prices','product_type_display']
    
    def get_info(self, obj):
        clean_text = re.sub(r'<[^>]+>', '', obj.info)  
        clean_text = unescape(clean_text)              
        return clean_text.strip()
    
    
    def get_prices(self, obj):
        latest_price = obj.product_prise.filter(amount__gt=0, price__gt=0).order_by('-id').first()
        if latest_price:
            return {
                'price': latest_price.price,
                # 'amount': latest_price.amount
            }
        return None
    
    
    def get_product_type_display(self, obj):
        if obj.product_type == "Рецепт билан":
            return {
                'text': 'Рецептурный',
               
            }
        return {
                'text': 'Без рецепта',
                
            }
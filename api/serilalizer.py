from rest_framework import serializers
from Product.models import *

from tmp.models import *
from . utls import * 



class OurPharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurPharmacie
        fields = ['id', 'title', 'address', 'shift', 'phone_number', 'lat', 'lon']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['price', 'amount', 'unique_identifier']


class ProductSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField() 
    product_type_display = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Product
        fields = ['id', 'name','producer','country','prices','image1','product_type_display','info']
    
    def get_info(self, obj):
        raw_text = getattr(obj, 'info', '')
        cleaned_text = sanitize_text(raw_text)
        parts = split_text(cleaned_text)
        return parts 

    
    def get_image1(self, obj):
        if obj.image1 and hasattr(obj.image1, 'url'):
            return f"https://akmalfarm.uz{obj.image1.url}"
        return None
    
    def get_prices(self, obj):
        latest_price = obj.product_prise.filter(amount__gt=0, price__gt=0).order_by('-id').first()
        if latest_price:
            return {
                'price': latest_price.price,
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

   
class ProductpageSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(many=True) 
    image1 = serializers.SerializerMethodField()
    product_type_display = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'prices', 'image1',  'product_type_display']
    
    
    def get_product_type_display(self, obj):
        if obj.product_type == "Рецепт билан":
            return {
                'text': 'Рецептурный',
               
            }
        return {
                'text': 'Без рецепта',
                
            }
    
    def get_image1(self, obj):
        if obj.image1 and hasattr(obj.image1, 'url'):
            return f"https://akmalfarm.uz{obj.image1.url}"
        return None
 
    
class CategoryallSerializer(serializers.ModelSerializer):
    filtered_products = ProductpageSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'filtered_products']
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']
        depth = True


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Order
        fields ='__all__'
        

class DastafcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dostafca
        fields = ['amount']


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = ['id','name', 'address']
        
class BlogSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = ['id', 'image', 'title', 'text', 'created_at']
        
    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return f"https://akmalfarm.uz{obj.image.url}"
        return None
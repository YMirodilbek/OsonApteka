from tmp.models import Landlord, Applicant
from rest_framework import serializers
from Product.models import *
from tmp.models import *
from . utls import * 

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"


class OurPharmacieSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurPharmacie
        fields = ['id', 'title', 'address', 'shift', 'phone_number', 'lat', 'lon']


class CategorySerializer(serializers.ModelSerializer):
    svg = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_svg(self, obj):
        if obj.svg and hasattr(obj.svg, 'url'):
            return f"https://akmalfarm.uz{obj.svg.url}"
        return None


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['price', 'amount', 'unique_identifier']


class ProductSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField() 
    product_type_display = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    
    class Meta:
        model = Product  
        fields = ['id', 'name','producer','country','member','prices','category_person',
                  'image1','is_wishlist','product_type_display','info']
        depth = True
    
    def get_is_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).select_related('product').exists()
        return False
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
    # image1 = serializers.SerializerMethodField()
    product_type_display = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'prices', 'image1_url', 'is_wishlist', 'product_type_display',
                  'category_person']

    def get_is_wishlist(self, obj):
        return getattr(obj, 'is_wishlist', False)
    
    def get_product_type_display(self, obj):
        if obj.product_type == "Рецепт билан":
            return {'text': 'Рецептурный'}
        return {'text': 'Без рецепта'}

   
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
    product = ProductSerializer(many=False)
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']
        def get_product(self, obj):
            context = self.context
            return ProductSerializer(obj.product, context=context).data


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = '__all__'
        depth = True
    
    def get_total_price(self, obj):
        return obj.price * obj.quantity

    def get_product(self,obj):
         return ProductSerializer(obj.product).data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
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
    
    
class CheckoutSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all())
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHODS)
    address_text = serializers.CharField(required=False, allow_blank=True)
    phone_number1 = serializers.CharField()
    phone_number2 = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['filial', 'payment_method', 'address_text', 'phone_number1', 'phone_number2']


class VirtualCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualCard
        fields = '__all__'
        read_only_fields = ['user', 'card_number', 'cvv', 'created_at', 'updated_at']
    

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id','room_id','user','image','content','timestamp','is_read']
        # depth = 1
        extra_kwargs = {
            'content': {'required': False},
            'image': {'required': False},
        }
        

class LandlordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landlord
        fields = "__all__"


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"
        
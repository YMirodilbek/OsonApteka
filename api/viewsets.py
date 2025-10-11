from django.db.models import Case, When, BooleanField, Value, Count, Q, Prefetch, Sum, F, OuterRef, Subquery
from rest_framework.permissions import  AllowAny, IsAuthenticated
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.pagination import PageNumberPagination
from main.bot_messages import send_telegram_message
from Product.lotin_krill import  latin_to_cyrillic
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework import viewsets
from tmp.models import OurPharmacie
from difflib import SequenceMatcher
from rest_framework import filters
from rest_framework import status
from datetime import datetime
from Product.models import *
from . serilalizer import * 
import logging
import os
from difflib import SequenceMatcher

class OurPharmacieViewSet(viewsets.ModelViewSet):
    serializer_class = OurPharmacieSerializer
    queryset = OurPharmacie.objects.all()
    http_method_names = ['get'] 

    def similar(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get('search')
        if search:
            search_cyr = latin_to_cyrillic(search).lower()
            words = search_cyr.split()
            ids = set()

            for obj in queryset:
                title = obj.title.lower()
                address = obj.address.lower()

                for word in words:
                    if word in title or word in address:
                        ids.add(obj.id)
                        break
                    elif self.similar(word, title) >= 0.3 or self.similar(word, address) >= 0.3:
                        ids.add(obj.id)
                        break

            queryset = queryset.filter(id__in=ids)

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        Our = OurPharmacie.objects.get(id=id)
        serializer = OurPharmacieSerializer(Our, many=False)
        return Response(serializer.data)

   
class SearchProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if not search:
            return Product.objects.none()

        # Latin -> Cyrillic
        search = latin_to_cyrillic(search)

        # asosiy queryset (faqat narxi > 0 bo‘lgan mahsulotlar)
        product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)
        queryset = Product.objects.filter(
            product_prise__in=product_price_qs,
            name__isnull=False
        ).select_related('category').prefetch_related(
            Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
        ).distinct()

        # TrigramSimilarity bilan annotatsiya
        trigram_qs = queryset.annotate(
            similarity=TrigramSimilarity('name', search)
        ).filter(similarity__gt=0.1).order_by('-similarity')  # threshold pastroq qilindi

        if trigram_qs.exists():
            return trigram_qs[:6]
        return queryset.filter(name__icontains=search)[:6]


class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    
    def get_queryset(self):
        querset =  Wishlist.objects.filter(user=self.request.user)
        return querset
        
    
    def list(self, request):
        wishlist_product_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
        serializer = self.get_serializer(
            self.get_queryset(), many=True,
            context={'request': request, 'wishlist_product_ids': wishlist_product_ids}
        ) 
        return Response(serializer.data)
    
    def retrieve(self, request, pk ):
        return Response(
            WishlistSerializer(
                Wishlist.objects.get(id=pk)
            ).data
        )
    
    @action(methods=['post'], detail=False, serializer_class=WishlistSerializer)
    def wishlist_create(self, request):
        product_id = request.data.get('product')

        if not product_id:
            return Response({'error': 'Mahsulot ID kerak'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

            if created:
                return Response({'success': True})
            else:
                return Response({'success': False, 'message': 'Allaqachon mavjud'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Mahsulot topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    @action(methods=['delete'], detail=True, serializer_class=WishlistSerializer)
    def wishlist_delete(self,request, pk ):
        try:
            w = Wishlist.objects.get(id=int(pk))
            w.delete()
            return Response({
                'success': True
                })
        except:    
            return Response({
                'success': False
                })


class CategoryProductsViewSet(viewsets.ViewSet):
    http_method_names = ['get']

    def list(self, request):
        category_name = request.query_params.get('category')
        page = request.query_params.get("page", 1)

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        # 1. Faqat narxi va mavjudligi bor product price queryset
        product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)

        # 2. Asosiy products queryset (narxlar bilan) - hali annotate qilmaymiz
        products_qs = Product.objects.filter(
            product_prise__in=product_price_qs,
            name__isnull=False
        ).exclude(name='').order_by('id').distinct().select_related('category').prefetch_related(
            Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
        )

        # 3. Wishlist bilan annotate qilish faqat user auth bo‘lsa
        wishlist_product_ids = set()
        if request.user.is_authenticated:
            wishlist_product_ids = set(
                Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
            )
            products_qs = products_qs.annotate(
                is_wishlist=Case(
                    When(id__in=wishlist_product_ids, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        else:
            # User authentifikatsiyadan o'tmagan bo'lsa, barcha uchun False
            products_qs = products_qs.annotate(
                is_wishlist=Value(False, output_field=BooleanField())
            )

        # 4. Categories queryset, product_count bilan filter
        categories_qs = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__in=products_qs))
        ).filter(product_count__gt=0)

        if category_name:
            categories_qs = categories_qs.filter(name=category_name)

        # 5. Cheklangan miqdorda productlarni Prefetch qilish
        categories_qs = categories_qs.prefetch_related(
                Prefetch(
                    'products',
                    queryset=products_qs.order_by('id').distinct()[:50],  # duplication yo‘q
                    to_attr='filtered_products'
                )
            )
        # 6. Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(categories_qs, request)

       
        serializer = CategoryallSerializer(result_page, many=True,
                                           context={
                                    'request': request,
                                    'wishlist_product_ids': wishlist_product_ids
                                }
                                           )
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, pk):
        try:
            product = Product.objects.get(id=int(pk))

            # Default bo'sh set
            wishlist_product_ids = set()

            # Faqat login qilingan foydalanuvchi uchun wishlistni olish
            if request.user.is_authenticated:
                wishlist_product_ids = set(
                    Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
                )

            serializer = ProductSerializer(
                product,
                many=False,
                context={'request': request, 'wishlist_product_ids': wishlist_product_ids}
            )
            return Response(serializer.data)

        except Product.DoesNotExist:
            return Response({'success': False}, status=404)

    
    @action(detail=False, methods=['get'])
    def product(self, request):
        page = request.query_params.get("page", 1)

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        # faqat narxi va mavjudligi bor product price lar
        product_price_qs = ProductPrice.objects.filter(
            product_id=OuterRef("pk"),
            amount__gt=0,
            price__gt=0
        ).order_by("-id")

        # annotate bilan oxirgi price ni query darajasida olib kelamiz
        products_qs = (
            Product.objects.filter(name__isnull=False)
            .exclude(name="")
            .annotate(latest_price=Subquery(product_price_qs.values("price")[:1]))
            .select_related("category")
        )

        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(products_qs, request)

        # wishlist optimizatsiya
        wishlist_ids = set()
        if request.user.is_authenticated:
            wishlist_ids = set(
                Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)
            )

        serializer = ProductASerializer(
            result_page,
            many=True,
            context={"request": request, "wishlist_ids": wishlist_ids},
        )
        return paginator.get_paginated_response(serializer.data)
  
    @action(detail= False, methods=['get'])     
    def member(self, request):
        member = request.query_params.get('member')
        product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)

        products_qs = Product.objects.filter(
            product_prise__in=product_price_qs,
            name__isnull=False, member__name=member
        ).exclude(name='').order_by('id').distinct().select_related('category','member').prefetch_related(
            Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
        )
        return Response(
            ProductSerializer(products_qs, many=True).data
        )

    
class OrderViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def list(self, request):
        order = Order.objects.filter(user= request.user, is_paid=True).order_by('-id')
        return Response(
            OrderASerializer(
                order, many=True
            ).data
        )
    
    @action(detail=False, methods=['get'])
    def cart(self, request):
        user = request.user

        cart_items = OrderItem.objects.filter(
            order__user=user,
            order__is_completed=False
        ).select_related('product', 'order').order_by('price')
        
        wishlist_ids = set(
        Wishlist.objects.filter(user=user).values_list('product_id', flat=True)
         )
        serializer = OrderItemSerializer(cart_items, many=True,
                                           context={'request': request, 'wishlist_ids': wishlist_ids}
                                           )

        cart_total = sum([item['total_price'] for item in serializer.data])
        cart_count = len(serializer.data)

        return Response({
            "cart_items": serializer.data,
            "cart_total": cart_total,
            "cart_count": cart_count,
        
        })


    def retrieve(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs['pk'])
        
        return Response(
            OrderSerializer(
                order, many=False
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    
    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk):
        product = get_object_or_404(Product, id=pk)

        if product.product_type == "Рецепт билан":
            return Response({"status": 300 , 'Рецепт билан':'Рецепт билан'}, status=status.HTTP_200_OK)

        try:
            price = int(request.data.get('price') or 0)
        except (TypeError, ValueError):
            price = 0

        if price <= 0:
            price_obj = product.product_prise.filter(price__gt=0).order_by('price').first()
            price = price_obj.price if price_obj else 0

        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)

        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            price=price,
            name=product.name,
        )

        if not created:
            order_item.quantity += 1
            order_item.save()

        # cart = cart_context(request)
        # cart_count = len(cart['cart_items'])
        # cart_total = cart['cart_total']

        return Response({
            "status": 200,
            # "cart_count": cart_count,
            # "cart_total": cart_total
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def minus_from_cart(self, request, pk):
        product = get_object_or_404(Product, id=pk)

        try:
            order = Order.objects.get(user=request.user, is_completed=False)
        except Order.DoesNotExist:
            return Response({"status": 404, "message": "Buyurtma topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_item = OrderItem.objects.get(order=order, product=product)
        except OrderItem.DoesNotExist:
            return Response({"status": 404, "message": "Mahsulot savatchada yo'q."}, status=status.HTTP_404_NOT_FOUND)

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()

        return Response({
            "status": 200,
            "message": "Mahsulot soni yangilandi yoki o'chirildi."
        }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        order = Order.objects.filter(user=request.user, is_completed=False).first()

        if not order:
            return Response({"detail": "Savatingiz bo'sh."}, status=status.HTTP_400_BAD_REQUEST)

        order_item = OrderItem.objects.filter(order=order, product=product).first()

        if not order_item:
            return Response({"detail": "Mahsulot savatda yo'q."}, status=status.HTTP_400_BAD_REQUEST)

        order_item.delete()

        # cart = cart_context(request)
        # cart_count = len(cart['cart_items'])
        # cart_total = cart['cart_total']

        return Response({
            "status": 200,

        }, status=status.HTTP_200_OK)

        
class BlogViewset(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-id')[:4]
    serializer_class = BlogSerializer
    http_method_names = ['get']  
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        blogs = Blog.objects.all().order_by('-id')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        return Response(BlogSerializer(
            Blog.objects.get(id=id),many=False
        ).data)


class MemberViewset(viewsets.ModelViewSet):
    serializer_class =  MemberSerializer
    queryset = Member.objects.all()
    http_method_names = ['get']  


class VirtualCardViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VirtualCardSerializer
    def get_queryset(self):
        return VirtualCard.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        # Agar userda allaqachon karta mavjud bo‘lsa, uni qaytaramiz
        if VirtualCard.objects.filter(user=user).exists():
            card = VirtualCard.objects.get(user=user)
            serializer = self.get_serializer(card)
            return Response(
                {"detail": "Sizda allaqachon karta mavjud", "card": serializer.data},
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ChatViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    def get_queryset(self):
        return Chat.objects.filter(room_id=self.request.user.id).order_by('id')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.update(is_read=True)  # barcha xabarlarni o‘qildi deb belgilaydi
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def create(self, request, *args, **kwargs):
        user = request.user
        content = request.data.get('content')
        image = request.data.get('image')

        chat = Chat.objects.create(
            room_id=user.id,
            user=user,
            content=content,
            image=image,
            is_read = True
        )

        serializer = self.get_serializer(chat)

        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    

    def destroy(self, request, *args, **kwargs):
        try:
            chat = Chat.objects.get(id =kwargs['pk'])
            if chat.image and os.path.isfile(chat.image.path):
                os.remove(chat.image.path)
            chat.delete()
            return Response({'success': True, } )
        except:
            return Response({ 'success': False,} )
    
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            content = data.get('content')
            id = kwargs.get('pk')
            chat = Chat.objects.get(id=id)
            chat.content = content
            chat.save()
            

            response = {
                'success': True,
                'data': ChatSerializer(chat, many=False).data
            }
        except Exception as err:
            response = {
                'success': False,
                'error': str(err)
            }
            return Response(response, status=400)
        return Response(response)


class VacancyVievSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().order_by('-id')
    serializer_class = VacancySerializer
    http_method_names = ['get']  

@api_view(['POST'])
def catalog(request):
    id = request.data.get("id")

    products = Product.objects.filter(member__id=id)\
        .distinct()\
        .select_related('category', 'member')\
        .prefetch_related('product_prise')
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

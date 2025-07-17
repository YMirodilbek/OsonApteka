from  rest_framework.permissions import  AllowAny, IsAuthenticated
from django.db.models import Sum, F, Prefetch , Count , Q
from rest_framework.pagination import PageNumberPagination
from Product.lotin_krill import  latin_to_cyrillic
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from tmp.models import OurPharmacie
from rest_framework import filters
from rest_framework import status
from Product.models import *
from . serilalizer import * 


class OurPharmacieViewSet(viewsets.ModelViewSet):
    queryset = OurPharmacie.objects.all()
    serializer_class = OurPharmacieSerializer
    http_method_names = ['get'] 
    
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        Our = OurPharmacie.objects.get(id=id)
        serializer = OurPharmacieSerializer(Our, many=False)
        return Response(serializer.data)

   
class SearchProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)
        queryset = Product.objects.filter(
        product_prise__in=product_price_qs,  
        name__isnull=False
    ).distinct().select_related('category').prefetch_related(
        Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
    )

        search = self.request.query_params.get('search')
        if search:
            search = latin_to_cyrillic(search)
            queryset = queryset.filter(name__icontains=search)
        return queryset


class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    
    def list(self, request):
        return Response(WishlistSerializer(
            Wishlist.objects.filter(user=request.user) ,many=True
        ).data)
    
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
    # permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def list(self, request):
        category_name = request.query_params.get('category')
        page = request.query_params.get("page", 1)

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)

        products_qs = Product.objects.filter(
            product_prise__in=product_price_qs,
            name__isnull=False
        ).exclude(name='').order_by('id').distinct().select_related('category').prefetch_related(
            Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
        )

        categories_qs = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__in=products_qs))
        ).filter(product_count__gt=0)

        if category_name:
            categories_qs = categories_qs.filter(name=category_name)

        categories_qs = categories_qs.prefetch_related(
            Prefetch('products', queryset=products_qs, to_attr='filtered_products_all')
        )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(categories_qs, request)

        for category in result_page:
            category.filtered_products = category.filtered_products_all[:50]

        serializer = CategoryallSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, pk):
        try:
            product = Product.objects.get(id=int(pk))
            seralizer = ProductSerializer(product, many=False)
            return Response(seralizer.data)
        except:
            return Response({
                'success': False
                })
    
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
        order = Order.objects.filter(user= request.user)
        return Response(
            OrderSerializer(
                order, many=True
            ).data
        )
    
    @action(detail=False, methods=['get'])
    def cart(self, request):
        user = request.user

        cart_items = OrderItem.objects.filter(
            order__user=user,
            order__is_completed=False
        ).select_related('product', 'order')

        serializer = OrderItemSerializer(cart_items, many=True)

        cart_total = sum([item['total_price'] for item in serializer.data])
        cart_count = len(serializer.data)

        return Response({
            "cart_items": serializer.data,
            "cart_total": cart_total,
            "cart_count": cart_count
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

        cart = cart_context(request)
        cart_count = len(cart['cart_items'])
        cart_total = cart['cart_total']

        return Response({
            "status": 200,
            "cart_count": cart_count,
            "cart_total": cart_total
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

        cart = cart_context(request)
        cart_count = len(cart['cart_items'])
        cart_total = cart['cart_total']

        return Response({
            "status": 200,
            "cart_count": cart_count,
            "cart_total": cart_total
        }, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['post'])
    def delete_order_item(self, request, item_id):
        try:
            order_item = OrderItem.objects.get(id=item_id, order__user=request.user, order__is_completed=False)
        except OrderItem.DoesNotExist:
            return Response({"detail": "Bunday buyurtma elementi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        
        order_item.delete()

        cart = cart_context(request)
        cart_count = len(cart['cart_items'])
        cart_total = cart['cart_total']

        return Response({
            "status": 200,
            "cart_count": cart_count,
            "cart_total": cart_total
        }, status=status.HTTP_200_OK)
        
    
class BlogViewset(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-id')[:4]
    serializer_class = BlogSerializer
    http_method_names = ['get']  
    
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        return Response(BlogSerializer(
            Blog.objects.get(id=id),many=False
        ).data)


class MemberViewset(viewsets.ModelViewSet):
    serializer_class =  MemberSerializer
    queryset = Member.objects.all()
    http_method_names = ['get']  
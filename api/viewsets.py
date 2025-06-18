from rest_framework.response import Response
from rest_framework import viewsets
from tmp.models import OurPharmacie
from rest_framework import filters
from .serilalizer import * 
from Product.lotin_krill import  latin_to_cyrillic
class OurPharmacieViewSet(viewsets.ModelViewSet):
    queryset = OurPharmacie.objects.all()
    serializer_class = OurPharmacieSerializer
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        Our = OurPharmacie.objects.get(id=id)
        serializer = OurPharmacieSerializer(Our, many=False)
        return Response(serializer.data)

   
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get('search')
        if search:
            search = latin_to_cyrillic(search)
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
from django.urls import path
from .views import *
urlpatterns=[
    path('operator/',Operator),
    path('vacancy/',Vacancy),
    path('pharm/',Pharm),
    path('about/',About),
    path('policy/',Policy),
    path('conditions/',Conditions),
    path('public/',Public),
    path('resipe/',Resipe),
    path('landlords/',Landlords),
    path('vacancies/',Vacancies),
]
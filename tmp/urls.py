from django.urls import path
from .views import *
urlpatterns=[
    path('operator/',Operator, name='operator_url'),
    path('vacancy/',Vacancy, name='vacancy_url'),
    path('pharm/',Pharm, name='pharm_url'),
    path('about/',About, name='about_url'),
    path('policy/',Policy, name='policy_url'),
    path('conditions/',Conditions, name='conditions_url'),
    path('public/',Public, name='public_url'),
    path('resipe/',Resipe, name='resipe_url'),
    path('landlords/',Landlords, name='landlords_url'),
]
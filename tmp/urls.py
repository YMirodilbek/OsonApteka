from django.urls import path
from .views import *
urlpatterns=[
    # Old URLs
    path('vacancy/', Vacancy, name='vacancy_url'),
    path('vacancy/application/', VacancyApplication, name='vacancy_application_url'),
    path('vacancy/application/apteka/', ApplicantViwe, name='VacancyApplication_apteka_url'),
    
    path('pharm/', Pharm, name='pharm_url'),
    path('about/', About, name='about_url'),
    path('public/', Public, name='public_url'),
    path('landlords/', Landlords, name='landlords_url'),
    path('blog/',blog_view, name='blog'),
    path('blog/<int:pk>/', BlogDetail, name='blog_details'),

    
    
    # Dashboard URLs
    path('dashboard/', dashboard, name='dashboard_url'),
    path('dashboard/vacancy/', dashboard_vacancy, name='dashboard_vacancy_url'),
    path('dashboard/vacancy/application/', dashboard_vacany_application, name='dashboard_vacany_application_url'),
    path('dashboard/vacancy/application/delete/<int:id>/', dashboard_vacancy_application_delete, name='dashboard_vacancy_application_delete_url'),
    path('dashboard/pharmacy/', dashboard_pharmacy, name='dashboard_pharmacy_url'),
    path('dashboard/landlords/', dashboard_landlords, name='dashboard_landlords_url'),
    path('dashboard/about/', dashboard_about, name='dashboard_about_url'),
    path('dashboard/about/<int:id>/', dashboard_about_detail, name='dashboard_about_detail_url'),
    path('dashboard/about/video/', dashboard_about_video, name='dashboard_about_video_url'),
    path('dashboard/about/video/update/', dashboard_about_video_update, name='dashboard_about_video_update_url'),

    path('dashboard/public/', dashboard_public, name='dashboard_public_url'),
    path('dashboard/blog/', dashboard_blog, name='dashboard_blog'),

    # CRUD URLs
    path('vacancy/create/', vacancyCreate, name='vacancyCreate'),
    path('vacancy/update/<int:id>/', vacancyUpdate, name='vacancyUpdate'),
    path('vacancy/delete/<int:id>/', vacancyDelete, name='vacancyDelete'),
    
    path('pharmacy/create/', pharmCreate, name='pharmCreate'),
    path('pharmacy/update/<int:id>/', pharmUpdate, name='pharmUpdate'),
    path('pharmacy/delete/<int:id>/', pharmDelete, name='pharmDelete'),
    
    path('landlords/update/<int:id>/', landlordUpdate, name='landlordUpdate'),
    path('landlords/delete/<int:id>/', landlordDelete, name='landlordDelete'),
    
    path('about/update/<int:id>/', aboutUpdate, name='aboutUpdate'),
    path('about/create/', aboutCreate, name='aboutCreate'),
    path('about/delete/<int:id>/', aboutDelete, name='aboutDelete'),

    path('public/update/', publicUpdate, name='publicUpdate'),
    
    path('blog/create/', blog_create, name='blog_create'),
    path('blog/update/<int:id>/', blog_update, name='blog_update'),
    path('blog/delete/<int:id>/', blog_delete, name='blog_delete'),
]
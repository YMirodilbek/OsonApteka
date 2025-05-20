from typing import Any
from django.db import models


class OurPharmacie(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    lat = models.FloatField(default=0)
    lon = models.FloatField(default=0)

    def __str__(self):
        return self.title


class Landlord(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number_1 = models.CharField(max_length=255)
    phone_number_2 = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    age = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    

class AboutUs(models.Model):
    body = models.TextField()

    def __str__(self):
        return "About Us"
    

class Public(models.Model):
    body = models.TextField()

    def __str__(self):
        return "Public"


class Blog(models.Model):
    image = models.ImageField(upload_to='blog/')
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def delete(self, using=None, keep_parents=False):
        self.image.delete(save=False)
        return super().delete(using, keep_parents)

    def save(self, *args, **kwargs):
        if self.pk:
            old_image = Blog.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                old_image.delete(save=False)

        super().save(*args, **kwargs)
    


"""ClothesFinderServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import ClothesSearchApp.views as clothes_views

urlpatterns = [
    path('admin', admin.site.urls),
    path('clothes', clothes_views.ClothesView.as_view()),
    path('detailed', clothes_views.DetailedClothesView.as_view()),
    path('favourites', clothes_views.FavouriteClothesView.as_view()),
    path('colors/<str:cloth_type>', clothes_views.ColorView.as_view()),
    path('types', clothes_views.TypeView.as_view()),
    path('sizes', clothes_views.SizeView.as_view()),
    path('auth', clothes_views.CustomAuthToken.as_view()),
    path('register', clothes_views.UserCreateAPI.as_view()),
    path('occasions', clothes_views.OccasionView.as_view()),
    path('email', clothes_views.email_favourites)
]

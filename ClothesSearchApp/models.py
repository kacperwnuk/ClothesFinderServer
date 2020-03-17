from django.contrib.auth.models import User
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Size(models.Model):
    S = 'S'
    M = 'M'
    L = 'L'
    XL = 'XL'
    XXL = 'XXL'
    SIZES = [
        (S, S),
        (M, M),
        (L, L),
        (XL, XL),
        (XXL, XXL)]
    name = models.CharField(max_length=50, unique=True, blank=False, null=False, choices=SIZES)

    def __str__(self):
        return self.name


class Clothes(models.Model):
    key = models.CharField(max_length=50, null=False, blank=False, unique=True)
    type = models.CharField(max_length=100, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    sizes = models.ManyToManyField(Size)
    colors = models.ManyToManyField(Color)


class DetailedClothes(models.Model):
    clothes = models.OneToOneField(Clothes, blank=False, null=False, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='')
    composition = models.CharField(max_length=100, default='')
    img_link = models.URLField(null=False)


class TypeColors(models.Model):
    T_SHIRT = 'T-SHIRT'
    SHIRT = 'SHIRT'
    PANTS = 'PANTS'
    SHORTS = 'SHORTS'
    JACKET = 'JACKET'
    SWEATER = 'SWEATER'
    TYPES = [
        (T_SHIRT, 'T-Shirty'),
        (SHIRT, 'Koszule'),
        (PANTS, 'Spodnie'),
        (SHORTS, 'Szorty'),
        (JACKET, 'Marynarki'),
        (SWEATER, 'Swetry'),
    ]
    cloth_type = models.CharField(choices=TYPES, max_length=10)
    colors = models.ManyToManyField(Color)

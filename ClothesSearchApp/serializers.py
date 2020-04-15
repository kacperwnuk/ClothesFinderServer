from django.contrib.auth.models import User
from rest_framework import serializers

from ClothesSearchApp.models import DetailedClothes, Clothes, Color, Shop, Type, Size, Occasion


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name']
        model = Shop


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name']
        model = Color


class ClothesSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(slug_field='name', queryset=Shop.objects.all())
    type = serializers.SlugRelatedField(slug_field='name', queryset=Type.objects.all())
    colors = serializers.SlugRelatedField(many=True, queryset=Color.objects.all(), slug_field='name')
    sizes = serializers.SlugRelatedField(many=True, queryset=Size.objects.all(), slug_field='name')

    class Meta:
        fields = ['key', 'name', 'price', 'shop', 'type', 'colors', 'sizes', 'img_link']
        model = Clothes


class OccasionSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field='name', queryset=Type.objects.all())
    color = serializers.SlugRelatedField(slug_field='name', queryset=Color.objects.all())
    size = serializers.SlugRelatedField(slug_field='name', queryset=Size.objects.all())

    class Meta:
        fields = '__all__'
        model = Occasion


class DetailedClothesSerializer(serializers.ModelSerializer):
    # clothes = ClothesSerializer()
    key = serializers.CharField(source='clothes.key')
    name = serializers.CharField(source='clothes.name')
    price = serializers.CharField(source='clothes.price')
    type = serializers.CharField(source='clothes.type')
    img_link = serializers.URLField(source='clothes.img_link')
    shop = serializers.SerializerMethodField(method_name='get_shop_name')
    sizes = serializers.SerializerMethodField(method_name='get_size_names')
    colors = serializers.SerializerMethodField(method_name='get_color_names')

    # clothes = ClothesSerializer()
    class Meta:
        fields = ['description', 'type', 'composition', 'img_link', 'shop', 'key', 'price', 'name', 'sizes',
                  'colors']
        # fields = ['description', 'composition', 'clothes']
        model = DetailedClothes

    def get_shop_name(self, obj):
        return obj.clothes.shop.name

    def get_size_names(self, obj):
        return [size.name for size in obj.clothes.sizes.all()]

    def get_color_names(self, obj):
        return [color.name for color in obj.clothes.colors.all()]


class TypeSerializer(serializers.ModelSerializer):
    colors = serializers.SlugRelatedField(many=True, queryset=Color.objects.all(), slug_field='name')

    class Meta:
        fields = ['name', 'colors']
        model = Type


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name']
        model = Size

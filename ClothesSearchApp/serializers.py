from rest_framework import serializers

from ClothesSearchApp.models import DetailedClothes, Clothes, Color, Shop, Type, Size


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
    colors = serializers.SlugRelatedField(many=True, queryset=Color.objects.all(), slug_field='name')
    sizes = serializers.SlugRelatedField(many=True, queryset=Size.objects.all(), slug_field='name')

    class Meta:
        fields = ['key', 'name', 'price', 'shop', 'type', 'colors', 'sizes', 'img_link']
        model = Clothes


class DetailedClothesSerializer(serializers.ModelSerializer):
    # clothes = ClothesSerializer()
    key = serializers.CharField(source='clothes.key')
    name = serializers.CharField(source='clothes.name')
    price = serializers.CharField(source='clothes.price')
    type = serializers.CharField(source='clothes.type')
    img_link = serializers.URLField(source='clothes.img_link')
    shop = serializers.SerializerMethodField(method_name='get_shop_name')

    class Meta:
        fields = ['clothes', 'description', 'type', 'composition', 'img_link', 'shop', 'key', 'price', 'name']
        model = DetailedClothes

    def get_shop_name(self, obj):
        return obj.clothes.shop.name


class TypeSerializer(serializers.ModelSerializer):
    # colors = serializers.SlugRelatedField(many=True, queryset=Color.objects.all(), slug_field='name')

    class Meta:
        fields = ['name']
        model = Type

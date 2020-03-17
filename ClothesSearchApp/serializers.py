from rest_framework import serializers

from ClothesSearchApp.models import DetailedClothes, Clothes, Color, Shop, TypeColors


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

    class Meta:
        fields = ['key', 'name', 'price', 'shop', 'type', 'colors']
        model = Clothes


class DetailedClothesSerializer(serializers.ModelSerializer):
    # clothes = ClothesSerializer()
    key = serializers.CharField(source='clothes.key')
    name = serializers.CharField(source='clothes.name')
    price = serializers.CharField(source='clothes.price')
    type = serializers.CharField(source='clothes.type')
    shop = serializers.SerializerMethodField(method_name='get_shop_name')

    class Meta:
        fields = ['clothes', 'description', 'type', 'composition', 'img_link', 'colors', 'shop', 'key', 'price', 'name']
        model = DetailedClothes

    def get_shop_name(self, obj):
        return obj.clothes.shop.name


class TypeColorsSerializer(serializers.ModelSerializer):
    colors = serializers.SlugRelatedField(many=True, queryset=Color.objects.all(), slug_field='name')

    class Meta:
        fields = ['colors']
        model = TypeColors
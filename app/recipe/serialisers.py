from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """serialiser for ingredient"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """ serialiser for recipe"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minute', 'price',
                  'tags', 'ingredients', 'link')
        read_only_Fields = ('id')

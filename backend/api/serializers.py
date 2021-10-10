from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Recipe, RecipeIngredient, Ingredient, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    id = serializers.PrimaryKeyRelatedField(write_only=True,
                                            source='ingredient',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_in_shopping_cart')
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(source='ingredients_to_recipe',
                                             many=True, read_only=True)

    author = UserSerializer(read_only=True)

    def get_current_user(self):
        user = self.context['request'].user
        return user

    def get_favorited(self, obj):
        user = self.get_current_user()
        return obj.is_favorited(user)

    def get_in_shopping_cart(self, obj):
        user = self.get_current_user()
        return obj.is_in_shopping_cart(user)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class RecipePostSerializer(ModelSerializer):
    ingredients = RecipeIngredientPostSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients:
            ingredient = ingredient_data.get('ingredient')
            amount = ingredient_data.get('amount')

            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)
        return recipe

    @staticmethod
    def create_ingredients(ingredients, recipe):
        recipe.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe, amount=ingredient.get('amount'),
                ingredient=ingredient.get('ingredient'))

        return True

    def to_representation(self, instance):
        """
        Переопределя
        """
        request_context = self.context['request']
        return RecipeSerializer(instance,
                                context={'request': request_context}).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')

        self.create_ingredients(ingredients,
                                instance)

        return super(RecipePostSerializer, self).update(instance,
                                                        validated_data)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'author', 'tags', 'image', 'name', 'text',
            'cooking_time')

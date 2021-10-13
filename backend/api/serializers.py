from django.contrib.auth import get_user_model
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer
from .models import Recipe, RecipeIngredient, Ingredient, Tag, Favorite

User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    id = serializers.PrimaryKeyRelatedField(write_only=True,
                                            source='ingredient',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FilteredListSerializer(serializers.ListSerializer):
    """
    Фильтрация вложенной стукрутры - рецепты - при запросе к подпискам юзера
    с параметром recipes_limit

    Один из вариантов. Отказался от него, все же мы просто делаем лимит, а не
    прям фильтруем по параметрам вложеность, а потом устанавлиаем лимит.
    """

    def to_representation(self, data):
        if not self.context.get('view').basename == 'user':
            return super(FilteredListSerializer, self).to_representation(data)
        search = self.context['request'].GET.get('recipes_limit')
        if search:
            data = data[:search]

        return super(FilteredListSerializer, self).to_representation(data)


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited', read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_in_shopping_cart', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(source='ingredients_to_recipe',
                                             many=True)

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
        # list_serializer_class = FilteredListSerializer
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
        """
        обрабатываем поля many to many
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    # @staticmethod
    # def setup_eager_loading(queryset):
    #     queryset = queryset.select_related('creator')

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """
        создаем записи в промежуточной таблице ингредиентов для рецепта
        """

        recipe.ingredients.clear()
        for ingredient in ingredients:
            (RecipeIngredient.objects.create(
                recipe=recipe, amount=ingredient.get('amount'),
                ingredient=ingredient.get('ingredient')))

    def to_representation(self, instance):
        """
        Переопределяем для того, чтобы вернуть не плоские представления
        tags и ingredients, как это нужно по ТЗ + дополнительные поля
        Так, как будто мы делаем get запрос на только что созданный рецепт
        """
        request_context = self.context['request']
        return RecipeSerializer(instance,
                                context={'request': request_context}).data

    def update(self, instance, validated_data):
        """
        При обновлении обработать нужно только записи в промежуточной таблице
        """
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


class SubRecipesSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes_count

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        return obj.is_subscribes(user)

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        if limit:
            recipes = obj.recipes_limit(limit)
        else:
            recipes = obj.recipes.all()
        return SubRecipesSerializer(recipes, many=True).data

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count')

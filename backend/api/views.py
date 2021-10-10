# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Recipe, Tag, Favorite, Ingredient
from .serializers import (RecipeSerializer, RecipePostSerializer,
                          TagSerializer, IngredientSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteView(APIView):
    """
    Учитывая, что мы ничего не принимаем кроме query params и не возвращаем,
    я посчитал наличие favorite сериалайзера избыточым
    """

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        obj, create = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if create:
            return Response(status=status.HTTP_201_CREATED)
        error = {'error': 'Рецепт уже есть в избранном'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user
        favorite_recipe = user.favorite_recipes.filter(recipe=recipe)
        if favorite_recipe:
            favorite_recipe.first().delete()
            Response(status=status.HTTP_204_NO_CONTENT)

        error = {'error': 'Такого рецепта нет в избранном'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

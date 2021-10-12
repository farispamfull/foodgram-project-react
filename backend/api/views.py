# Create your views here.
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.utils import Util
from .filters import RecipeFilter, IngredientFilter
from .models import Recipe, Tag, Favorite, Ingredient, ShoppingCart
from .paginators import StandardResultsSetPagination
from .permissions import AuthorOrIsAuthenticatedPermission
from .serializers import (RecipeSerializer, RecipePostSerializer,
                          TagSerializer, IngredientSerializer,
                          SubRecipesSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrIsAuthenticatedPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'ingredients',
            'tags',
            'author',
            'ingredients_to_recipe__ingredient'
        )

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            Recipe.objects.prefetch_related
            ("ingredients", "ingredients_to_recipe").filter(
                recipe_shopping_cart__user=request.user).order_by(
                "ingredients__name").values(
                "ingredients__name", "ingredients__measurement_unit").annotate(
                total=Sum("ingredients_to_recipe__amount"))
        )

        text = Util.make_shopping_text(ingredients)
        response = HttpResponse(
            text, content_type='application/text charset=utf-8'
        )
        response[
            'Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'
        return response


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class FavoriteView(APIView):
    """
    Учитывая, что мы ничего не принимаем кроме query params и не возвращаем,
    я посчитал наличие favorite сериалайзера избыточным
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubRecipesSerializer

    def get_object(self, id):
        return get_object_or_404(Recipe, id=id)

    def get(self, request, recipe_id):
        recipe = self.get_object(id=recipe_id)
        user = request.user

        obj, create = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if create:
            serializer = self.serializer_class(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = {'errors': 'Рецепт уже есть в избранном'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        recipe = self.get_object(id=recipe_id)
        user = request.user
        favorite_recipe = user.favorite_recipes.filter(recipe=recipe)
        if favorite_recipe:
            favorite_recipe.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        error = {'errors': 'Такого рецепта нет в избранном'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class ShoppingView(APIView):
    serializer_class = SubRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        return get_object_or_404(Recipe, id=id)

    def get(self, request, recipe_id):
        recipe = self.get_object(recipe_id)
        user = request.user

        obj, create = ShoppingCart.objects.get_or_create(user=user,
                                                         recipe=recipe)
        if create:
            serializer = self.serializer_class(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = {'errors': 'Рецепт уже есть в корзине покупок'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        recipe = self.get_object(recipe_id)
        user = request.user
        shopping_recipe = user.shopping_cart.filter(recipe=recipe)
        if shopping_recipe:
            shopping_recipe.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        error = {'errors': 'Такого рецепта нет в корзине покупок'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

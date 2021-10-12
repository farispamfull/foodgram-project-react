from django_filters import rest_framework as filters

from api.models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author_id')
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(recipe_shopping_cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(favorite_users__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

from django.forms.fields import MultipleChoiceField
from django_filters import rest_framework as filters

from api.models import Recipe, Ingredient


class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True


class MultipleFilter(filters.MultipleChoiceFilter):
    field_class = MultipleField


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author_id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    tags = MultipleFilter(field_name='tags__slug',
                          lookup_expr='iexact')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is True:
            user = self.request.user
            return queryset.filter(recipe_shopping_cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value is True:
            user = self.request.user
            return queryset.filter(favorite_users__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']

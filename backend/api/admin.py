from django.contrib import admin

from .models import Recipe, Favorite, RecipeIngredient, Ingredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    ordering = ['name']


@admin.register(RecipeIngredient)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount',)
    search_fields = ('ingredient__name', 'recipe__name')
    list_filter = ('recipe__name', 'ingredient__name')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    filter_horizontal = ('tags',)
    list_filter = ('author', 'name', 'tags',)
    list_display = (
        'name', 'author', 'favorite', 'count_ingredients','pub_date'
    )
    search_fields = ('name', 'author', 'tags__name')
    ordering = ['pub_date']

    # autocomplete_fields = ('ingredients',)

    def count_ingredients(self, obj):
        count = RecipeIngredient.objects.filter(recipe=obj).count()
        return count

    def favorite(self, obj):
        count = Favorite.objects.filter(recipe=obj).count()
        return count

    count_ingredients.short_description = 'количество ингредиентов'
    favorite.short_description = 'добавили в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')

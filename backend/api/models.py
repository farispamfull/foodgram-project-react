from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, db_index=True)
    color = models.CharField(max_length=15)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tag'
            )]


class Ingredient(models.Model):
    title = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipe/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    ordering = ["-pub_date"]
    verbose_name = 'Рецепты'
    verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='recipes')
    amount = models.PositiveIntegerField(default=1)


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="recipe_shopping_cart")


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_users',
        verbose_name='Любимый автор'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Любимый рецепт'
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]

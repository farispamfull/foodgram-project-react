from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.views import user_logout, LoginView
from users.views import UserViewSet,SubscriptionsView
from .views import (RecipesViewSet, TagsViewSet, FavoriteView,
                    IngredientsViewSet,ShoppingView)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipesViewSet, basename='recipe')
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('tags', TagsViewSet, basename='tag')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredient')
auth_patterns = [
    path('token/logout/',
         user_logout,
         name='user_logout'),
    path('token/login/',
         LoginView.as_view(),
         name='login_user'), ]

urlpatterns = [
    path('recipes/<int:recipe_id>/shopping_cart/',ShoppingView.as_view()),
    path('users/<int:user_id>/subscriptions/',SubscriptionsView.as_view()),
    path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    path('auth/', include(auth_patterns)),
    path('', include(router_v1.urls)),

]

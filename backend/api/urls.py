from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.views import user_logout, LoginView
from users.views import UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
auth_patterns = [
    path('token/logout/',
         user_logout,
         name='user_logout'),
    path('token/login/',
         LoginView.as_view(),
         name='login_user'), ]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router_v1.urls)),

]

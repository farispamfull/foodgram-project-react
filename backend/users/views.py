from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Follow
from api.serializers import SubSerializer
from .models import User
from .serializers import (UserSerializer, ChangePasswordSerializer,
                          )


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return ChangePasswordSerializer
        if self.action == 'subscriptions':
            return SubSerializer
        else:
            return UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        users = User.objects.filter(following__user=request.user)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class SubscriptionsView(APIView):

    def get(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)

        obj, create = Follow.objects.get_or_create(user=user, author=author)
        if create:
            serializer = SubSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = {'error': 'Вы уже подписаны на этого автора'}
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        author = get_object_or_404(User, pk=user_id)
        user = request.user
        follow_obj = user.follower.filter(author=author)
        if follow_obj:
            follow_obj.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {'errors': 'Вы не подписаны на этого автора'}
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

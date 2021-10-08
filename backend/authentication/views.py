from django.contrib.auth import logout as django_logout, get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import UserLoginSerializer

fb = get_user_model()


class LoginView(GenericAPIView):
    serializer_class = UserLoginSerializer
    token = None

    def get_response(self):
        data = {'auth_token': self.token}
        return Response(data, status=status.HTTP_201_CREATED)

    def login(self):
        user = self.serializer.validated_data['user']
        self.token = Token.objects.get_or_create(user=user)[0].key

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


@api_view(['POST'])
def user_logout(request):
    request.user.auth_token.delete()
    django_logout(request)
    return Response(status=status.HTTP_201_CREATED)

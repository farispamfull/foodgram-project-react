from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

fb = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(password=password, email=email)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'Account disabled, contact admin')

        data['user'] = user
        return data

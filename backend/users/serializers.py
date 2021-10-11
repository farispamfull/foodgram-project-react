from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers




User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        print(user)

        return obj.is_subscribes(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'password', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True,
                                     'validators': [validate_password]},
                        'id': {'read_only': True}}
        model = User

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user





class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        validators=[validate_password],
        required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, data):
        current_password = data['current_password']
        user = self.context['request'].user
        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Неверный пароль"})
        return data

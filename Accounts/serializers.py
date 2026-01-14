# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# ------------------- Register Serializer -------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # profile_image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'password','email']  # Only these fields required

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')  # email is optional
        )
        return user

# ------------------- Custom Token Serializer -------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                
                "email": self.user.email,
                "phone_number": self.user.phone_number,
                "is_staff": self.user.is_staff,
                  "profile_image": (
                self.user.profile_image.url
                if self.user.profile_image
                else None
            ),
                "allowed_to_post": self.user.allowed_to_post
            }
        })
        return data

# ------------------- Update User Serializer -------------------
class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_image','first_name', 'last_name', 'allowed_to_post','phone_number', 'is_active', 'is_staff']
        read_only_fields = ['allowed_to_post']  # optional, only admin can change
class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number','email', 'password', 'allowed_to_post', 'is_active', 'is_staff']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # hash password
        instance.save()
        return instance
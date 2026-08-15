from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import UserProfile, get_user_role


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur."""

    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_role(self, obj):
        return get_user_role(obj)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur."""

    role = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='profile.phone_number', required=False, allow_blank=True)
    company_name = serializers.CharField(source='profile.company_name', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'company_name', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def get_role(self, obj):
        return get_user_role(obj)

    def update(self, instance, validated_data):
        # Extract profile data
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.phone_number = profile_data.get('phone_number', profile.phone_number)
            profile.company_name = profile_data.get('company_name', profile.company_name)
            profile.save()
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription publique."""

    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['ADMIN', 'OWNER'], required=False, default='OWNER')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'role'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})

        role = data.get('role', 'OWNER')
        if role not in ['ADMIN', 'OWNER']:
            raise serializers.ValidationError({"role": "Le rôle doit être ADMIN ou OWNER."})

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError({"username": "Ce nom d'utilisateur est déjà pris."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role', 'OWNER')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': role},
        )
        return user


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur par un administrateur."""

    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['ADMIN', 'OWNER'], required=False, default='OWNER')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name', 'role', 'is_active'
        ]

    def validate(self, data):
        role = data.get('role', 'OWNER')
        if role not in ['ADMIN', 'OWNER']:
            raise serializers.ValidationError({"role": "Le rôle doit être ADMIN ou OWNER."})

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError({"username": "Ce nom d'utilisateur est déjà pris."})

        return data

    def create(self, validated_data):
        role = validated_data.pop('role', 'OWNER')
        is_active = validated_data.get('is_active', True)
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = is_active
        user.save()
        
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': role},
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        identifier = data.get('username')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Identifiants incorrects ou compte inactif.")

        user = None
        if '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            user = User.objects.filter(username__iexact=identifier).first()

        if user is not None and user.is_active and user.check_password(password):
            return {'user': user}

        raise serializers.ValidationError("Identifiants incorrects ou compte inactif.")


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe."""

    old_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return data

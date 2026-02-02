from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from equipment_api.models import EquipmentDataset, EquipmentRecord, Token


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        token = Token.objects.create(user=user)
        return {'user': user, 'token': token}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'],
            password=attrs['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        token, _ = Token.objects.get_or_create(user=user)
        return {'user': user, 'token': token}


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField(source='token.key')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')


class EquipmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRecord
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    records = EquipmentRecordSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentDataset
        fields = [
            'id', 'name', 'uploaded_at', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution', 'records'
        ]


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for history listing (no records)."""
    class Meta:
        model = EquipmentDataset
        fields = [
            'id', 'name', 'uploaded_at', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution'
        ]

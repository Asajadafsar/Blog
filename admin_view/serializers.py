from rest_framework import serializers
from sign.models import User,BlogPost,Comment,Tag,Category
import hashlib



class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'role', 'registration_date', 'profile_picture']

    def create(self, validated_data):
        # Hash the password before saving
        if 'password' in validated_data:
            validated_data['password'] = hashlib.sha256(validated_data['password'].encode()).hexdigest()
        return super().create(validated_data)
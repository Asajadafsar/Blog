from django.conf import settings
from rest_framework import serializers
from sign.models import User, BlogPost, Category,Tag,Comment
import hashlib
from .models import AdminLogs

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'role', 'registration_date', 'profile_picture']

    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = hashlib.sha256(validated_data['password'].encode()).hexdigest()
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile_picture:
            if request is not None:
                host = request.get_host()
                representation['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
            else:
                representation['profile_picture'] = f"{settings.DEFAULT_HOST}{instance.profile_picture.url}"
        return representation

class AdminLogsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='log_id', read_only=True)

    class Meta:
        model = AdminLogs
        fields = ['id', 'action', 'action_date', 'ip_address']

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='category_id', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag_id', read_only=True)
    username = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'username', 'post_title', 'status']


class BlogPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='post_id', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    user = serializers.CharField(source='user.username', read_only=True)

    blog_images = serializers.ImageField(required=False)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'blog_images', 'created_at', 'updated_at', 'user', 'category', 'status', 'tags']
        read_only_fields = ['created_at', 'updated_at', 'user', 'tags']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.blog_images:
            if request is not None:
                representation['blog_images'] = request.build_absolute_uri(instance.blog_images.url)
            else:
                representation['blog_images'] = f"{settings.DEFAULT_HOST}{instance.blog_images.url}"
        return representation



class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='comment_id', read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'updated_at', 'user_id', 'post_id']


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag_id', read_only=True)
    added_by = serializers.CharField(source='user_id.username', read_only=True)  
    post_title = serializers.CharField(source='post_id.title', read_only=True)  
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'added_by', 'post_title', 'status']
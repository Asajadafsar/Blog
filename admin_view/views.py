from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from functools import wraps
import jwt
from .models import AdminLogs
from sign.models import User,BlogPost,Comment,Tag,Category
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .serializers import AdminLogsSerializer,BlogPostSerializer,CategorySerializer,BlogPostSerializer,CommentSerializer,TagSerializer



# JWT secret key (should be securely stored)
SECRET_KEY = 'your_secret_key'

# Token verification decorator
def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'error': 'Authorization header is missing'}, status=401)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(pk=payload['user_id'])
            request.user = user
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token is expired'}, status=401)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper



#add log def
def add_log(action, ip_address):
    AdminLogs.objects.create(action=action, action_date=timezone.now(), ip_address=ip_address)



#view all user and add user
@api_view(['GET', 'POST'])
def manage_users(request):
    if request.method == 'GET':
        # Your existing GET logic here
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Your existing POST logic here
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            ip_address = request.META.get('REMOTE_ADDR')
            add_log('add user', ip_address)  # Log the action
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 


#edit and delete ann get user_id
@api_view(['GET', 'PUT', 'DELETE'])
def manage_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            ip_address = request.META.get('REMOTE_ADDR')
            add_log('edit user', ip_address)  # Log the action
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ip_address = request.META.get('REMOTE_ADDR')
        add_log('delete user', ip_address)  # Log the action
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




#view all logs and delete
@api_view(['GET', 'DELETE'])
def manage_logs(request, log_id=None):
    if request.method == 'GET':
        logs = AdminLogs.objects.all()
        serializer = AdminLogsSerializer(logs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        try:
            log = AdminLogs.objects.get(pk=log_id)
        except AdminLogs.DoesNotExist:
            return Response({'error': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)
        log.delete()
        return Response({'message': 'Log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


#manage post
@api_view(['GET'])
def manage_blog_posts(request):
    if request.method == 'GET':
        # Retrieve all blog posts
        blog_posts = BlogPost.objects.all()
        serializer = BlogPostSerializer(blog_posts, many=True)
        return Response(serializer.data)


#manage post
@api_view(['GET', 'PUT', 'DELETE'])
def manage_blog_post(request, post_id):
    try:
        blog_post = BlogPost.objects.get(post_id=post_id)
    except BlogPost.DoesNotExist:
        return Response({'error': 'Blog post not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Retrieve a specific blog post by post_id
        serializer = BlogPostSerializer(blog_post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Update an existing blog post
        serializer = BlogPostSerializer(blog_post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            ip_address = request.META.get('REMOTE_ADDR')
            add_log('edit blog post', ip_address)  # Log the action
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete an existing blog post
        blog_post.delete()
        ip_address = request.META.get('REMOTE_ADDR')
        add_log('delete blog post', ip_address)  # Log the action
        return Response(status=status.HTTP_204_NO_CONTENT)





#manage comment
@api_view(['GET', 'DELETE'])
def manage_comment(request, comment_id=None):
    if request.method == 'GET':
        if comment_id is not None:
            # Retrieve a specific comment by comment_id
            try:
                comment = Comment.objects.get(comment_id=comment_id)
                serializer = CommentSerializer(comment)
                return Response(serializer.data)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all comments
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
    elif request.method == 'DELETE':
        if comment_id is not None:
            # Delete an existing comment
            try:
                comment = Comment.objects.get(comment_id=comment_id)
                ip_address = request.META.get('REMOTE_ADDR')
                add_log('delete comment', ip_address)
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Comment.DoesNotExist:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Please provide a comment_id'}, status=status.HTTP_400_BAD_REQUEST)


#manage tag
@api_view(['GET','PUT', 'DELETE'])
def manage_tag(request, tag_id=None):
    ip_address = request.META.get('REMOTE_ADDR')

    if request.method == 'GET':
        if tag_id is not None:
            # Retrieve a specific tag by tag_id
            try:
                tag = Tag.objects.get(tag_id=tag_id)
                serializer = TagSerializer(tag)
                return Response(serializer.data)
            except Tag.DoesNotExist:
                return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all tags
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)

    elif request.method == 'PUT':
        if tag_id is not None:
            # Update an existing tag
            try:
                tag = Tag.objects.get(tag_id=tag_id)
                serializer = TagSerializer(tag, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    add_log('update tag', ip_address)
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Tag.DoesNotExist:
                return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Please provide a tag_id'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if tag_id is not None:
            # Delete an existing tag
            try:
                tag = Tag.objects.get(tag_id=tag_id)
                tag.delete()
                add_log('delete tag', ip_address)
                return Response({'message': 'Tag deleted successfully', 'id': tag_id}, status=status.HTTP_204_NO_CONTENT)
            except Tag.DoesNotExist:
                return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Please provide a tag_id'}, status=status.HTTP_400_BAD_REQUEST)



#manage_categories 
@api_view(['GET', 'POST'])
def manage_categories(request):
    ip_address = request.META.get('REMOTE_ADDR')
    
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            add_log('create category', ip_address)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#manage_categories 
@api_view(['GET', 'PUT', 'DELETE'])
def manage_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    ip_address = request.META.get('REMOTE_ADDR')
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            add_log('edit category', ip_address)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        add_log('delete category', ip_address)
        return Response(status=status.HTTP_204_NO_CONTENT)






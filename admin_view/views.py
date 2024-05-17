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
from .serializers import AdminLogsSerializer



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
        ip_address = request.META.get('REMOTE_ADDR')
        add_log('delete log', ip_address)  # Log the action before deletion
        log.delete()
        return Response({'message': 'Log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)







#manage post
#get list all posts
@csrf_exempt
@token_required
def get_blog_posts(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Parse request parameters
    sort_field, sort_order = request.GET.get('sort', 'post_id,ASC').split(',')
    filter_query = request.GET.get('filter', '{}')
    range_header = request.headers.get('Range', '0-9')

    # Process sort parameters
    if sort_field == 'id':
        sort_field = 'post_id'
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'ASC'  # Default sorting order

    # Process range parameters
    start, end = map(int, range_header.split('-'))

    # Build Q objects for filtering
    q_objects = Q()
    if filter_query:
        filter_dict = eval(filter_query)  # Convert filter string to dictionary
        if 'title' in filter_dict:
            q_objects &= Q(title__icontains=filter_dict['title'])
        if 'user__username' in filter_dict:
            q_objects &= Q(user__username__icontains=filter_dict['user__username'])
        if 'category__name' in filter_dict:
            q_objects &= Q(category__name__icontains=filter_dict['category__name'])

    # Perform the filtered query
    blog_posts_query = BlogPost.objects.filter(q_objects)

    # Apply sorting order
    sort_field = sort_field if sort_order == 'ASC' else f'-{sort_field}'  # Construct field name with sorting order
    blog_posts_query = blog_posts_query.order_by(sort_field)

    # Perform pagination
    paginator = Paginator(blog_posts_query, end - start + 1)
    blog_posts_page = paginator.get_page(start // (end - start + 1) + 1)

    # Serialize blog post data
    blog_posts_data = [{
        'id': post.post_id,
        'title': post.title,
        'image': request.build_absolute_uri(post.image.url) if post.image else None,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': post.user.user_id,
        'category_id': post.category.category_id,
        'status': post.status
    } for post in blog_posts_page]

    # Prepare response
    response = JsonResponse(blog_posts_data, status=200, safe=False)
    response['X-Total-Count'] = paginator.count
    response['Content-Range'] = f'blog_posts {start}-{end}/{paginator.count}'

    return response





#manage post
@csrf_exempt
@token_required
def manage_blog_post(request, post_id):
    if request.method == 'GET':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        try:
            # Retrieve the blog post by post_id
            post = BlogPost.objects.get(post_id=post_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Blog post not found'}, status=404)

        # Get all tags associated with the post
        tags = Tag.objects.filter(post_id=post_id)

        # Serialize blog post data
        post_data = {
            'id': post.post_id,
            'title': post.title,
            'content': post.content,
            'image': request.build_absolute_uri(post.image.url) if post.image else None,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': post.user.user_id,
            'category_id': post.category.category_id,
            'status': post.status,
            'tags': [tag.name for tag in tags]  # Serialize tag names
        }

        return JsonResponse(post_data, status=200)
    
    elif request.method == 'DELETE':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)
        
        # Check if the blog post exists
        post = BlogPost.objects.filter(post_id=post_id).first()
        if not post:
            return JsonResponse({'error': 'Blog post not found'}, status=404)
        
        # Delete the blog post's image file if it exists
        if post.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(post.image))
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete the blog post from the database
        post.delete()
        # Get the IP address of the user who deleted the blog post
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='delete blog post', ip_address=ip_address)
        return JsonResponse({'message': 'Blog post deleted successfully', 'id': post_id}, status=200)
    
    elif request.method == 'POST':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Retrieve the blog post to update
        try:
            post = BlogPost.objects.get(pk=post_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Blog post not found'}, status=404)

        # Parse request data
        data = request.POST

        # Update blog post fields if provided in the request
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.status = data.get('status', post.status)

        # Update category if provided
        category_id = data.get('category_id')
        if category_id:
            try:
                category = Category.objects.get(category_id=category_id)
                post.category = category
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Category not found'}, status=404)

        # Don't delete existing tags, just add new ones
        tags = request.POST.getlist('tags')  # Assuming tags are sent as a list of names or IDs
        if tags:
            for tag_name in tags:
                try:
                    # Check if tag with the given name exists
                    tag = Tag.objects.get(name=tag_name, post_id=post)
                except ObjectDoesNotExist:
                    # Create a new tag if it doesn't exist
                    tag = Tag.objects.create(name=tag_name, user_id=request.user, post_id=post)
        tags = Tag.objects.filter(post_id=post_id)

        # Save the updated blog post
        post.save()
        # Get the IP address of the user who added the new user
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='edit post', ip_address=ip_address)
        return JsonResponse({
            'id': post.post_id,
            'title': post.title,
            'content': post.content,
            'image': request.build_absolute_uri(post.image.url) if post.image else None,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': post.user.user_id,
            'category_id': post.category.category_id,
            'tags': [tag.name for tag in tags],
            'status': post.status
        }, status=200)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





#manage comment
#get comments list
@csrf_exempt
@token_required
def get_comments(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Ensure the logged-in user has admin role
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Insufficient privileges'}, status=403)

    # Parse request parameters
    sort_field, sort_order = request.GET.get('sort', 'comment_id,ASC').split(',')
    filter_query = request.GET.get('filter', '{}')
    range_header = request.GET.get('range', '0,9')

    # Process sort parameters
    if sort_field == 'id':
        sort_field = 'comment_id'
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'ASC'  # Default sorting order

    # Process range parameters
    start, end = map(int, range_header.split(','))

    # Build Q objects for filtering
    q_objects = Q()  # Empty Q object to start with
    if filter_query:
        filter_dict = eval(filter_query)  # Convert filter string to dictionary
        if 'user_id' in filter_dict:
            q_objects &= Q(user_id=filter_dict['user_id'])
        if 'post_id' in filter_dict:
            q_objects &= Q(post_id=filter_dict['post_id'])

    # Perform the filtered query
    comments_query = Comment.objects.filter(q_objects)

    # Apply sorting order
    sort_field = sort_field if sort_order == 'ASC' else f'-{sort_field}'  # Construct field name with sorting order
    comments_query = comments_query.order_by(sort_field)

    # Perform pagination
    paginator = Paginator(comments_query, end - start + 1)
    comments_page = paginator.get_page(start // (end - start + 1) + 1)

    # Extract comment data
    comments_data = [{
        'id': comment.comment_id,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': comment.user_id.user_id,
        'post_id': comment.post_id.post_id
    } for comment in comments_page]

    # Prepare response
    response = JsonResponse(comments_data, safe=False)
    response['X-Total-Count'] = paginator.count
    response['Content-Range'] = f'comments {start}-{end}/{paginator.count}'

    return response




#manage comment
@csrf_exempt
@token_required
def manage_comment(request, comment_id):
    if request.method == 'GET':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Retrieve the comment by comment_id
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)

        # Serialize comment data
        comment_data = {
            'id': comment.comment_id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': comment.user_id.user_id,
            'post_id': comment.post_id.post_id
        }

        return JsonResponse(comment_data, status=200)
    
    elif request.method == 'DELETE':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)
        
        # Check if the comment exists
        comment = Comment.objects.filter(comment_id=comment_id).first()
        if not comment:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        
        # Delete the comment from the database
        comment.delete()
        
        # Get the IP address of the user who added the new user
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='delete comment', ip_address=ip_address)
        # Optionally, perform additional cleanup actions here
        
        return JsonResponse({'message': 'Comment deleted successfully', 'id': comment_id}, status=200)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)






#manage tag
# Get all tags
@csrf_exempt
@token_required
def get_tags(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Parse request parameters
    sort_field, sort_order = request.GET.get('sort', 'tag_id,ASC').split(',')
    filter_query = request.GET.get('filter', '{}')
    range_header = request.headers.get('Range', '0-9')

    # Process sort parameters
    if sort_field == 'id':
        sort_field = 'tag_id'
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'ASC'  # Default sorting order

    # Process range parameters
    start, end = map(int, range_header.split('-'))

    # Build Q objects for filtering
    q_objects = Q()
    if filter_query:
        filter_dict = eval(filter_query)  # Convert filter string to dictionary
        if 'name' in filter_dict:
            q_objects &= Q(name__icontains=filter_dict['name'])
        if 'user__username' in filter_dict:
            q_objects &= Q(user_id__username__icontains=filter_dict['user__username'])
        if 'post__title' in filter_dict:
            q_objects &= Q(post_id__title__icontains=filter_dict['post__title'])

    # Perform the filtered query
    tags_query = Tag.objects.filter(q_objects)

    # Apply sorting order
    sort_field = sort_field if sort_order == 'ASC' else f'-{sort_field}'  # Construct field name with sorting order
    tags_query = tags_query.order_by(sort_field)

    # Perform pagination
    paginator = Paginator(tags_query, end - start + 1)
    tags_page = paginator.get_page(start // (end - start + 1) + 1)

    # Serialize tag data
    tags_data = [{
        'id': tag.tag_id,
        'name': tag.name,
        'user_id': tag.user_id.user_id,
        'post_id': tag.post_id.post_id,
        'status': tag.status
    } for tag in tags_page]

    # Prepare response
    response = JsonResponse(tags_data, status=200, safe=False)
    response['X-Total-Count'] = paginator.count
    response['Content-Range'] = f'tags {start}-{end}/{paginator.count}'

    return response



# Get tag by tag_id
@csrf_exempt
@token_required
def get_tag(request, tag_id):
    if request.method == 'GET':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Retrieve the tag by tag_id
        try:
            tag = Tag.objects.get(tag_id=tag_id)
        except Tag.DoesNotExist:
            return JsonResponse({'error': 'Tag not found'}, status=404)

        # Serialize tag data
        tag_data = {
            'id': tag.tag_id,
            'name': tag.name,
            'user_id': tag.user_id.user_id,
            'post_id': tag.post_id.post_id,
            'status': tag.status
        }

        return JsonResponse(tag_data, status=200)
    
    elif request.method == 'DELETE':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)
        
        # Check if the tag exists
        tag = Tag.objects.filter(tag_id=tag_id).first()
        if not tag:
            return JsonResponse({'error': 'Tag not found'}, status=404)
        
        # Delete the tag from the database
        tag.delete()
        
        # Get the IP address of the user who deleted the tag
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='delete tag', ip_address=ip_address)
        
        return JsonResponse({'message': 'Tag deleted successfully', 'id': tag_id}, status=200)
    
    elif request.method == 'POST':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Parse request data
        data = request.POST

        # Retrieve the existing tag by tag_id
        try:
            existing_tag = Tag.objects.get(tag_id=tag_id)
        except Tag.DoesNotExist:
            return JsonResponse({'error': 'Tag not found'}, status=404)

        # Retrieve the blog post by post_id
        post_id = data.get('post_id')
        try:
            post = BlogPost.objects.get(post_id=post_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        # Extract and validate tag name
        tag_name = data.get('name')
        if not tag_name:
            return JsonResponse({'error': 'Tag name is required'}, status=400)

        # Extract and validate user_id
        user_id = data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Update the existing tag with new data
        existing_tag.name = tag_name
        existing_tag.user_id = user
        existing_tag.post_id = post
        existing_tag.save()

        # Serialize updated tag data
        tag_data = {
            'id': existing_tag.tag_id,
            'name': existing_tag.name,
            'user_id': existing_tag.user_id.user_id,
            'post_id': existing_tag.post_id.post_id,
            'status': existing_tag.status
        }

        # Get the IP address of the user who updated the tag
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='update tag', ip_address=ip_address)

        return JsonResponse(tag_data, status=200)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



# Get all categories
@csrf_exempt
@token_required
def get_categories(request):
    if request.method == 'GET':
        # Parse request parameters
        sort_field, sort_order = request.GET.get('sort', 'category_id,ASC').split(',')
        filter_query = request.GET.get('filter', '{}')
        range_header = request.headers.get('Range', '0-9')

        # Process sort parameters
        if sort_field == 'id':
            sort_field = 'category_id'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'ASC'  # Default sorting order

        # Process range parameters
        start, end = map(int, range_header.split('-'))

        # Build Q objects for filtering
        q_objects = Q()
        if filter_query:
            filter_dict = eval(filter_query)  # Convert filter string to dictionary
            if 'name' in filter_dict:
                q_objects &= Q(name__icontains=filter_dict['name'])

        # Perform the filtered query
        categories_query = Category.objects.filter(q_objects)

        # Apply sorting order
        sort_field = sort_field if sort_order == 'ASC' else f'-{sort_field}'  # Construct field name with sorting order
        categories_query = categories_query.order_by(sort_field)

        # Perform pagination
        paginator = Paginator(categories_query, end - start + 1)
        categories_page = paginator.get_page(start // (end - start + 1) + 1)

        # Serialize category data
        categories_data = [{
            'id': category.category_id,
            'name': category.name,
        } for category in categories_page]

        # Prepare response
        response = JsonResponse(categories_data, status=200, safe=False)
        response['X-Total-Count'] = paginator.count
        response['Content-Range'] = f'categories {start}-{end}/{paginator.count}'

        return response

    elif request.method == 'POST':
        # Extract data from the request
        data = request.POST
        name = data.get('name')

        # Check if all required fields are provided
        if not name:
            return JsonResponse({'error': 'Name field is missing'}, status=400)

        # Create the category
        try:
            new_category = Category.objects.create(
                name=name
            )
            return JsonResponse({'id': new_category.category_id, 'name': name}, status=201)
            
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




@csrf_exempt
@token_required
def manage_category(request, category_id=None):
    if request.method == 'GET':
        # Retrieve the category by category_id
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)

        # Serialize category data
        category_data = {
            'category_id': category.category_id,
            'name': category.name
        }

        return JsonResponse(category_data, status=200)

    elif request.method == 'DELETE':
        # Check if the category exists
        category = Category.objects.filter(category_id=category_id).first()
        if not category:
            return JsonResponse({'error': 'Category not found'}, status=404)
        
        # Delete the category from the database
        category.delete()
        return JsonResponse({'message': 'Category deleted successfully', 'category_id': category_id}, status=200)

    elif request.method == 'POST':
        # Retrieve the category to update
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)

        # Parse request data
        data = request.POST

        # Update category name if provided in the request
        category.name = data.get('name', category.name)

        # Save the updated category
        category.save()
        return JsonResponse({'category_id': category.category_id, 'name': category.name}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
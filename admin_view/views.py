from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from functools import wraps
import jwt
from .models import AdminLogs
from sign.models import User,BlogPost
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.utils import timezone


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



def create_adminlogs(user, action, ip_address):
    new_log = AdminLogs.objects.create(user=user, action=action, action_date=timezone.now(), ip_address=ip_address)
    return new_log


#get list user
@csrf_exempt
@token_required
def get_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Ensure the logged-in user has admin role
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Insufficient privileges'}, status=403)

    # Parse request parameters
    sort_field, sort_order = request.GET.get('sort', 'user_id,ASC').split(',')
    filter_query = request.GET.get('filter', '{}')
    range_header = request.GET.get('range', '0,9')

    # Process sort parameters
    if sort_field == 'id':
        sort_field = 'user_id'
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'ASC'  # Default sorting order

    # Process range parameters
    start, end = map(int, range_header.split(','))

    # Build Q objects for filtering
    q_objects = Q(role='user')  # Only customers
    if filter_query:
        filter_dict = eval(filter_query)  # Convert filter string to dictionary
        if 'email' in filter_dict:
            q_objects &= Q(email__icontains=filter_dict['email'])
        if 'username' in filter_dict:
            q_objects &= Q(username__icontains=filter_dict['username'])
        if 'phone_number' in filter_dict:
            q_objects &= Q(phone_number__icontains=filter_dict['phone_number'])

    # Perform the filtered query
    users_query = User.objects.filter(q_objects)

    # Apply sorting order
    sort_field = sort_field if sort_order == 'ASC' else f'-{sort_field}'  # Construct field name with sorting order
    users_query = users_query.order_by(sort_field)

    # Perform pagination
    paginator = Paginator(users_query, end - start + 1)
    users_page = paginator.get_page(start // (end - start + 1) + 1)

    # Extract user data
    users_data = [{
        'id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'phone_number': user.phone_number,
        'registration_date': user.registration_date.strftime('%Y-%m-%d') if user.registration_date else None
    } for user in users_page]

    # Prepare response
    response = JsonResponse(users_data, safe=False)
    response['X-Total-Count'] = paginator.count
    response['Content-Range'] = f'customers {start}-{end}/{paginator.count}'

    return response




#add user
@csrf_exempt
@token_required
def add_user(request):
    if request.method == 'POST':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Extract data from the request
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone_number = data.get('phone_number')
        role = data.get('role')

        # Check if all required fields are provided
        if not all([username, password, email, role]):
            return JsonResponse({'error': 'One or more required fields are missing'}, status=400)

        # Check if user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User already exists'}, status=409)

        # Hash the password
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Save profile picture if provided
        profile_picture = request.FILES.get('profile_picture')
        profile_picture_path = None
        if profile_picture:
            profile_picture_path = default_storage.save('profile_pictures/' + profile_picture.name, ContentFile(profile_picture.read()))

        # Create the user
        try:
            new_user = User.objects.create(
                username=username,
                password=hashed_password,
                email=email,
                phone_number=phone_number,
                role=role,
                profile_picture=profile_picture_path,  # Save the path to the profile picture
                registration_date=datetime.now().date()
            )
            # Get the IP address of the user who added the new user
            ip_address = request.META.get('REMOTE_ADDR')
            # Create admin log
            create_adminlogs(user=request.user, action='Add user', ip_address=ip_address)
            return JsonResponse({'id': new_user.user_id, 'username': username, 'email': email, 'phone_number': phone_number, 'role': role, 'profile_picture':profile_picture_path}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




# delete user
@csrf_exempt
@token_required
def delete_user(request, user_id):
    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)
        
        # Check if the user exists
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Delete the user's profile picture file if it exists
        if user.profile_picture:
            profile_picture_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_picture))
            if os.path.exists(profile_picture_path):
                os.remove(profile_picture_path)

        # Delete the user from the database
        user.delete()
        # Get the IP address of the user who added the new user
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='delete user', ip_address=ip_address)
        return JsonResponse({'message': 'User deleted successfully', 'id': user_id}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




#edit user
@csrf_exempt
@token_required
def update_user(request, user_id):
    if request.method == 'POST':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Retrieve the user to update
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Parse request data
        data = request.POST

        # Update user fields if provided in the request
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.role = data.get('role', user.role)

        # Update the password if provided
        if 'password' in data:
            user.password = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()

        # Update profile picture if provided
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']

            # Delete previous profile picture if exists
            if user.profile_picture:
                file_path = os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)
                default_storage.delete(file_path)

            # Save the new profile picture to the media directory
            file_path = os.path.join(settings.MEDIA_ROOT, 'profile_pictures', profile_picture.name)
            default_storage.save(file_path, ContentFile(profile_picture.read()))

            # Update the user's profile picture path
            user.profile_picture = 'profile_pictures/' + profile_picture.name

        # Save the updated user
        user.save()
        # Get the IP address of the user who added the new user
        ip_address = request.META.get('REMOTE_ADDR')
        # Create admin log
        create_adminlogs(user=request.user, action='edit user', ip_address=ip_address)
        return JsonResponse({
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role,
            'registration_date': user.registration_date.strftime('%Y-%m-%d') if user.registration_date else None,
            'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
        }, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#get user/id
@csrf_exempt
@token_required
def get_user(request, user_id):
    if request.method == 'GET':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        # Retrieve the user by user_id
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Serialize user data
        user_data = {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role,
            'registration_date': user.registration_date.strftime('%Y-%m-%d') if user.registration_date else None,
            'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
        }

        return JsonResponse(user_data, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





#view logs
@csrf_exempt
@token_required
def view_admin_logs(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized access! Only admins can view logs'}, status=401)

    # Parse request parameters
    sort_field = request.GET.get('sort', 'log_id')
    sort_order = request.GET.get('order', 'ASC')
    filter_action = request.GET.get('action', None)
    filter_user_id = request.GET.get('user_id', None)

    # Query admin logs
    admin_logs = AdminLogs.objects.all()

    # Apply filters
    if filter_action:
        admin_logs = admin_logs.filter(action__icontains=filter_action)
    if filter_user_id:
        admin_logs = admin_logs.filter(user_id=filter_user_id)

    # Apply sorting
    if sort_order == 'DESC':
        sort_field = '-' + sort_field

    admin_logs = admin_logs.order_by(sort_field)

    # Serialize admin logs
    logs_data = [{
        'id': log.log_id,
        'user_id': log.user.user_id,
        'action': log.action,
        'action_date': log.action_date.strftime('%Y-%m-%d %H:%M:%S'),
        'ip_address': log.ip_address,
    } for log in admin_logs]

    return JsonResponse(logs_data, safe=False)




#delete logs
@csrf_exempt
@token_required
def delete_admin_log(request, log_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized access! Only admins can delete logs'}, status=401)

    # Find the log to delete
    try:
        log = AdminLogs.objects.get(log_id=log_id)
    except AdminLogs.DoesNotExist:
        return JsonResponse({'error': 'Log not found'}, status=404)

    # Delete the log
    log.delete()

    # Create admin log for the deletion
    create_adminlogs(request.user, 'Deleted log', request.META.get('REMOTE_ADDR'))

    return JsonResponse({'message': 'Log deleted successfully'}, status=200)





#get list all posts
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



#get post id
@csrf_exempt
@token_required
def get_blog_post(request, post_id):
    if request.method == 'GET':
        # Ensure the logged-in user has admin role
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Insufficient privileges'}, status=403)

        try:
            # Retrieve the blog post by post_id
            post = BlogPost.objects.get(post_id=post_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Blog post not found'}, status=404)

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
            'status': post.status
        }

        return JsonResponse(post_data, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#delete post
@csrf_exempt
@token_required
def delete_blog_post(request, post_id):
    if request.method == 'DELETE':
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
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#edit post
@csrf_exempt
@token_required
def update_blog_post(request, post_id):
    if request.method == 'POST':
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

        # Update the image if provided
        if 'image' in request.FILES:
            image_file = request.FILES['image']

            # Delete previous image if exists
            if post.image:
                file_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
                os.remove(file_path)

            # Save the new image to the media directory
            file_path = os.path.join(settings.MEDIA_ROOT, 'blog_images', image_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Update the blog post's image path
            post.image = 'blog_images/' + image_file.name

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
            'status': post.status
        }, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



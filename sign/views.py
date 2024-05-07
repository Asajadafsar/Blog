from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User,Category,BlogPost
import hashlib
import jwt
import json
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.core import serializers



# JWT secret key (should be securely stored)
SECRET_KEY = 'your_secret_key'
# python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

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

# register user
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        
        required_fields = ['username', 'password', 'email', 'phone_number']
        if all(field in data for field in required_fields):
            username = data['username']
            password = data['password']
            email = data['email']
            phone_number = data['phone_number']

            if User.objects.filter(username=username).exists():
                return HttpResponse('User already exists!', status=409)

            if any(data[field] == '' for field in required_fields):
                return HttpResponse('One or more required fields are empty!', status=400)

            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            user = User(username=username, password=hashed_password, email=email, phone_number=phone_number)
            user.save()

            # Generate JWT token
            token = jwt.encode({'user_id': user.user_id}, SECRET_KEY, algorithm='HS256')
            return JsonResponse({'token': token.decode('utf-8')})
        else:
            return HttpResponse('Required fields are missing!', status=400)
    else:
        return HttpResponse('Method not allowed!', status=405)

# login user
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        
        required_fields = ['username', 'password']
        if all(field in data for field in required_fields):
            identifier = data['username']  # Can be username or email
            password = data['password']
            
            # Check if the identifier is an email or username
            is_email = identifier.endswith('@gmail.com')

            if is_email:
                try:
                    # Attempt login with email
                    user = User.objects.get(email=identifier)
                except User.DoesNotExist:
                    return HttpResponse('Invalid email or password!', status=401)
            else:
                try:
                    # Attempt login with username
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    return HttpResponse('Invalid username or password!', status=401)

            # Verify password
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if user.password != hashed_password:
                return HttpResponse('Invalid password!', status=401)

            # Generate JWT token
            token = jwt.encode({'user_id': user.user_id}, SECRET_KEY, algorithm='HS256')
            return JsonResponse({'token': token})
        else:
            return HttpResponse('Required fields are missing!', status=400)
    else:
        return HttpResponse('Method not allowed!', status=405)


#view_profile
@csrf_exempt
@token_required
def profile(request):
    if request.method == 'GET':
        user = request.user
        return JsonResponse({'username': user.username, 'email': user.email, 'phone_number': user.phone_number, 'role': user.role})
    else:
        return HttpResponse('Method not allowed!', status=405)



# Edit profile
@csrf_exempt
@token_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        
        user = request.user

        # Update profile information
        if 'email' in data:
            user.email = data['email']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        
        user.save()

        return HttpResponse('Profile updated successfully!')
    else:
        return HttpResponse('Method not allowed!', status=405)


# Reset password
@csrf_exempt
@token_required
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)

        required_fields = ['new_password']
        if all(field in data for field in required_fields):
            user = request.user  # Get the authenticated user

            new_password = data['new_password']

            # Update user's password
            hashed_new_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            user.password = hashed_new_password
            user.save()

            return HttpResponse('Password reset successfully!')
        else:
            return HttpResponse('Required fields are missing!', status=400)
    else:
        return HttpResponse('Method not allowed!', status=405)



#view posts user
@csrf_exempt
@token_required
def user_posts(request):
    if request.method == 'GET':
        user = request.user
        posts = BlogPost.objects.filter(user_id=user.user_id)
        
        # Serialize posts into JSON format with required fields
        serialized_posts = []
        for post in posts:
            post_data = {
                'id': post.post_id,
                'title': post.title,
                'category': post.category.name,
                'image': post.image.url if post.image else None,
            }
            serialized_posts.append(post_data)
        
        return JsonResponse({'posts': serialized_posts})
    else:
        return HttpResponse('Method not allowed!', status=405)



@csrf_exempt
def display_post(request, post_id):
    if request.method == 'GET':
        try:
            # Get the post with the given id
            post = BlogPost.objects.get(post_id=post_id)
            
            # Prepare the response data
            post_data = {
                'title': post.title,
                'content': post.content,
                'image': post.image.url if post.image else None,  # Assuming image is stored in MEDIA_ROOT
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S")  # Format the datetime
            }
            
            # Return the response
            return JsonResponse(post_data)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#add post
@csrf_exempt
@token_required
def add_post(request):
    if request.method == 'POST':
        # Get user ID from the token
        user_id = request.user.user_id
        
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Extract data from JSON
        title = data.get('title')
        content = data.get('content')
        category_name = data.get('category_name')
        
        # Check if required fields are present
        if not all([title, content, category_name]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Extract image file from request.FILES
        image = request.FILES.get('image')

        try:
            # Fetch category object based on category name
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category does not exist'}, status=400)

        try:
            # Create new blog post
            new_post = BlogPost.objects.create(
                title=title,
                content=content,
                image=image,
                user_id=user_id,
                category=category
            )
            return JsonResponse({'success': 'Post added successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



# Edit existing blog posts
@csrf_exempt
@token_required
def edit_post(request, post_id):
    if request.method == 'PUT':
        # Get user ID from the token
        user_id = request.user.user_id
        
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Extract data from JSON
        title = data.get('title')
        content = data.get('content')
        category_name = data.get('category_name')
        
        # Check if required fields are present
        if not any([title, content, category_name]):
            return JsonResponse({'error': 'At least one field to edit is required'}, status=400)

        # Fetch the post to edit
        try:
            post = BlogPost.objects.get(post_id=post_id, user_id=user_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        # Update fields if provided
        if title:
            post.title = title
        if content:
            post.content = content
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                post.category = category
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Category does not exist'}, status=400)

        # Save the changes
        post.save()

        return JsonResponse({'success': 'Post updated successfully', 'post_id': post.post_id}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)






#delete post
@csrf_exempt
@token_required
def delete_post(request, post_id):
    if request.method == 'DELETE':
        user = request.user
        try:
            # Get the post to delete
            post = BlogPost.objects.get(post_id=post_id, user_id=user.user_id)
            post.delete()
            return JsonResponse({'success': 'Post deleted successfully'})
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
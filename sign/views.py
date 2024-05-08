from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import User,Category,BlogPost,Comment,Tag
import hashlib
import jwt
import json
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.core import serializers
from django.db.models import Q



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
            # Parse form data
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')

            # Check if all required fields are provided
            if not all([username, password, email, phone_number]):
                return HttpResponse('One or more required fields are missing!', status=400)

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                return HttpResponse('User already exists!', status=409)

            # Hash the password
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # Save the user
            user = User(username=username, password=hashed_password, email=email, phone_number=phone_number)
            user.save()

            # Check if profile picture is provided
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                # Save the profile picture
                user.profile_picture.save(profile_picture.name, profile_picture, save=True)

            # Generate JWT token
            token = jwt.encode({'user_id': user.user_id}, SECRET_KEY, algorithm='HS256')
            return JsonResponse({'token': token})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
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
        profile_picture_url = user.profile_picture.url if user.profile_picture else None
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'profile_picture': profile_picture_url,
            'role': user.role
        })
    else:
        return HttpResponse('Method not allowed!', status=405)



# # Edit profile
# @csrf_exempt
# @token_required
# def edit_profile(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return HttpResponse('Invalid JSON data!', status=400)
        
#         user = request.user

#         # Update profile information
#         if 'email' in data:
#             user.email = data['email']
#         if 'phone_number' in data:
#             user.phone_number = data['phone_number']
        
#         user.save()

#         return HttpResponse('Profile updated successfully!')
#     else:
#         return HttpResponse('Method not allowed!', status=405)

#edit profile
@csrf_exempt
@token_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            # Get the authenticated user
            user = request.user

            # Check if profile picture is provided for editing
            if 'new_profile_picture' in request.FILES:
                new_profile_picture = request.FILES['new_profile_picture']
                # Save the new profile picture
                user.profile_picture.delete()  # Delete the old profile picture
                user.profile_picture.save(new_profile_picture.name, new_profile_picture, save=True)

                return JsonResponse({'success': 'Profile picture updated successfully'})
            else:
                return HttpResponse('No profile picture provided for editing!', status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
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
            # Get tags associated with the post
            tags = Tag.objects.filter(post_id=post)
            # Extract tag names
            tag_names = [tag.name for tag in tags]
            post_data = {
                'id': post.post_id,
                'title': post.title,
                'category': post.category.name,
                'image': post.image.url if post.image else None,
                'tags': tag_names,
                'status': post.status  # Include the status field in the response
            }
            serialized_posts.append(post_data)
        
        return JsonResponse({'posts': serialized_posts})
    else:
        return HttpResponse('Method not allowed!', status=405)




#display_post and comment
@csrf_exempt
def display_post(request, post_id):
    if request.method == 'GET':
        try:
            # Get the post with the given id
            post = BlogPost.objects.get(post_id=post_id, status='active')  # Check if the status is 'active'
            
            # Fetch comments associated with the post
            comments = Comment.objects.filter(post_id=post_id)
            
            # Fetch tags associated with the post
            tags = Tag.objects.filter(post_id=post)
            
            # Serialize comments into JSON format
            serialized_comments = []
            for comment in comments:
                comment_data = {
                    'comment_id': comment.comment_id,
                    'content': comment.content,
                    'user_id': comment.user_id.username,
                    'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                serialized_comments.append(comment_data)
            
            # Serialize tags into JSON format
            serialized_tags = []
            for tag in tags:
                tag_data = {
                    'tag_id': tag.tag_id,
                    'name': tag.name
                }
                serialized_tags.append(tag_data)
            
            # Prepare the response data for the post, its comments, and tags
            post_data = {
                'title': post.title,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'comments': serialized_comments,  # Include comments in the response
                'tags': serialized_tags  # Include tags in the response
            }
            
            # Return the response with post details, comments, and tags
            return JsonResponse({'post': post_data})
        
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found or not published'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#add post
@csrf_exempt
@token_required
def add_post(request):
    if request.method == 'POST':
        try:
            # Parse form data
            title = request.POST.get('title')
            content = request.POST.get('content')
            category_name = request.POST.get('category_name')
            tags = request.POST.getlist('tags')
            image = request.FILES.get('image')

            # Check if required fields are provided
            if not all([title, content, category_name]):
                return JsonResponse({'error': 'One or more required fields are missing'}, status=400)

            # Get user ID from the token
            user_id = request.user.user_id

            # Fetch user object based on user_id
            user = User.objects.get(user_id=user_id)

            # Fetch category object based on category name
            category, created = Category.objects.get_or_create(name=category_name)

            # Create new blog post
            new_post = BlogPost.objects.create(
                title=title,
                content=content,
                image=image,
                user=user,
                category=category
            )

            # Add tags to the post
            for tag_name in tags:
                # Check if the tag already exists, if not, create it
                tag, created = Tag.objects.get_or_create(name=tag_name, user_id=user, post_id=new_post)

            return JsonResponse({'success': 'Post added successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



# edit post
@csrf_exempt
@token_required
def edit_post(request, post_id):
    if request.method == 'POST':
        # Get user ID from the token
        user_id = request.user.user_id
        
        # Check if the post exists
        try:
            post = BlogPost.objects.get(post_id=post_id, user_id=user_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        # Check if the post is active
        if post.status != 'active':
            return JsonResponse({'error': 'Post is not active'}, status=403)

        # Update fields if provided
        if 'title' in request.POST:
            post.title = request.POST['title']
        if 'content' in request.POST:
            post.content = request.POST['content']
        if 'category_name' in request.POST:
            category_name = request.POST['category_name']
            try:
                category = Category.objects.get(name=category_name)
                post.category = category
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Category does not exist'}, status=400)

        # Update image if provided
        if 'image' in request.FILES:
            post.image.delete()  # Delete the previous image
            post.image = request.FILES['image']
        
        # Save the changes to the post
        post.save()

        # Fetch the User object based on user_id
        user = User.objects.get(user_id=user_id)

        # Add new tags
        add_tags = request.POST.getlist('add_tag')
        for tag_name in add_tags:
            # Ensure tag name is not empty
            if tag_name:
                # Create the tag if it doesn't exist
                tag, created = Tag.objects.get_or_create(name=tag_name, user_id=user, post_id=post)
                # Optionally, you can set status or other fields for the tag here if needed

        # Delete tags
        delete_tags = request.POST.getlist('delete_tag')
        for tag_name in delete_tags:
            # Ensure tag name is not empty
            if tag_name:
                # Delete the tag if it exists
                Tag.objects.filter(name=tag_name, user_id=user, post_id=post_id).delete()
        
        return JsonResponse({'success': 'Post updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





# Delete post
@csrf_exempt
@token_required
def delete_post(request, post_id):
    if request.method == 'DELETE':
        user = request.user
        try:
            # Get the post to delete
            post = BlogPost.objects.get(post_id=post_id, user_id=user.user_id)
            # Delete associated tags
            Tag.objects.filter(post_id=post_id).delete()
            # Delete the post
            post.delete()
            return JsonResponse({'success': 'Post deleted successfully'})
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





#add comment
@csrf_exempt
@token_required
def add_comment(request, post_id):
    if request.method == 'POST':
        # Get the authenticated user
        user = request.user
        
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Extract content from JSON
        content = data.get('content')
        
        # Check if content is provided
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        try:
            # Check if the post exists and is active
            post = BlogPost.objects.get(post_id=post_id, status='active')
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Active post not found'}, status=404)

        try:
            # Create new comment
            new_comment = Comment.objects.create(
                content=content,
                user_id=user,
                post_id=post
            )
            return JsonResponse({'success': 'Comment added successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





#edit comment
@csrf_exempt
@token_required
def edit_comment(request, comment_id):
    if request.method == 'PUT':
        # Get the authenticated user
        user = request.user

        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Extract content from JSON
        content = data.get('content')

        # Check if content is provided
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        try:
            # Get the comment to edit
            comment = Comment.objects.get(comment_id=comment_id)

            # Check if the authenticated user is the owner of the comment
            if comment.user_id != user:
                return JsonResponse({'error': 'You are not allowed to edit this comment'}, status=403)

            # Update the comment content
            comment.content = content
            comment.save()

            return JsonResponse({'success': 'Comment updated successfully'}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#delete comment
@csrf_exempt
@token_required
def delete_comment(request, comment_id):
    if request.method == 'DELETE':
        # Get the authenticated user
        user = request.user

        try:
            # Get the comment to delete
            comment = Comment.objects.get(comment_id=comment_id)

            # Check if the authenticated user is the owner of the comment
            if comment.user_id != user:
                return JsonResponse({'error': 'You are not allowed to delete this comment'}, status=403)

            # Delete the comment
            comment.delete()

            return JsonResponse({'success': 'Comment deleted successfully'})

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




# add deraf post
@csrf_exempt
@token_required
def add_deraf_post(request):
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
        tags = data.get('tags', [])  # Get tags as a list
        
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
            # Fetch user object based on user_id
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=400)

        try:
            # Create new blog post with status as 'draft'
            new_post = BlogPost.objects.create(
                title=title,
                content=content,
                image=image,
                user=user,  # Use user instance instead of user_id
                category=category,
                status='draft'  # Set status to 'draft'
            )

            # Add tags to the post with status as 'draft'
            for tag_name in tags:
                # Check if the tag already exists, if not, create it
                tag, created = Tag.objects.get_or_create(name=tag_name, user_id=user, post_id=new_post, status='draft')
            
            return JsonResponse({'success': 'Draft post added successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




# edit_draft_post
@csrf_exempt
@token_required
def edit_draft_post(request, post_id):
    if request.method == 'PUT':
        # Get user ID from the token
        user_id = request.user.user_id
        
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        # Fetch the post to edit
        try:
            post = BlogPost.objects.get(post_id=post_id, user_id=user_id)
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

        # Check if the post is active
        if post.status == 'active':
            return JsonResponse({'error': 'Post is not Draft'}, status=403)

        # Update fields if provided
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        if 'category_name' in data:
            try:
                category = Category.objects.get(name=data['category_name'])
                post.category = category
            except Category.DoesNotExist:
                return JsonResponse({'error': 'Category does not exist'}, status=400)
        
        # Add new tags
        if 'add_tag' in data:
            for tag_name in data['add_tag']:
                # Get or create User instance for the tag
                user_instance = User.objects.get(user_id=user_id)
                tag, created = Tag.objects.get_or_create(name=tag_name, user_id=user_instance, post_id=post)

        # Delete tags
        if 'delete_tag' in data:
            for tag_name in data['delete_tag']:
                try:
                    tag = Tag.objects.get(name=tag_name, user_id=user_id, post_id=post)
                    tag.delete()
                except Tag.DoesNotExist:
                    pass  # Tag doesn't exist, no need to delete
        
        # Save the changes
        post.save()

        return JsonResponse({'success': 'Post Draft updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




# Publish draft post
@csrf_exempt
@token_required
def publish_draft_post(request, post_id):
    if request.method == 'PUT':
        # Get the authenticated user
        user = request.user

        try:
            # Get the draft post
            post = BlogPost.objects.get(post_id=post_id, user_id=user.user_id, status='draft')
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Draft post not found'}, status=404)

        # Change the status of the draft post to 'active' (published)
        post.status = 'active'
        post.save()

        # Update the status of tags associated with the post to 'active'
        tags = Tag.objects.filter(post_id=post)
        tags.update(status='active')

        return JsonResponse({'success': 'Draft post published successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# Unpublish post (change status to draft)
@csrf_exempt
@token_required
def unpublish_post(request, post_id):
    if request.method == 'PUT':
        # Get the authenticated user
        user = request.user

        try:
            # Get the active post
            post = BlogPost.objects.get(post_id=post_id, user_id=user.user_id, status='active')
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Active post not found'}, status=404)

        # Change the status of the post to 'draft'
        post.status = 'draft'
        post.save()

        # Update the status of tags associated with the post to 'draft'
        tags = Tag.objects.filter(post_id=post)
        tags.update(status='draft')

        return JsonResponse({'success': 'Post unpublished successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



# Display draft posts with their tags
@csrf_exempt
def display_draft_posts(request):
    if request.method == 'GET':
        # Get all draft posts
        draft_posts = BlogPost.objects.filter(status='draft')

        # Serialize draft posts and their tags
        serialized_draft_posts = []
        for post in draft_posts:
            # Get tags associated with the post
            tags = Tag.objects.filter(post_id=post)

            # Serialize tags into JSON format
            serialized_tags = []
            for tag in tags:
                tag_data = {
                    'tag_id': tag.tag_id,
                    'name': tag.name
                }
                serialized_tags.append(tag_data)

            # Prepare the response data for the draft post and its tags
            post_data = {
                'post_id': post.post_id,
                'title': post.title,
                'content': post.content,
                'tags': serialized_tags
            }

            serialized_draft_posts.append(post_data)

        return JsonResponse({'draft_posts': serialized_draft_posts})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



# Search for active posts by title, username(author), or content
@csrf_exempt
def search_active_posts(request):
    if request.method == 'GET':
        # Get search query parameters from the request
        search_query = request.GET.get('q', '')

        # Search for active posts matching the search query
        active_posts = BlogPost.objects.filter(
            Q(content__icontains=search_query) | 
            Q(title__icontains=search_query) | 
            Q(user__username__icontains=search_query),
            status='active'
        ).distinct()

        # Serialize active posts with required information
        serialized_active_posts = []
        for post in active_posts:
            # Get tags associated with the post
            tags = Tag.objects.filter(post_id=post)

            # Serialize tags into JSON format
            serialized_tags = []
            for tag in tags:
                tag_data = {
                    'tag_id': tag.tag_id,
                    'name': tag.name
                }
                serialized_tags.append(tag_data)

            # Prepare the response data for the active post
            post_data = {
                'post_id': post.post_id,
                'title': post.title,
                'category': post.category.name,
                'image': post.image.url if post.image else None,
                'tags': serialized_tags
            }

            serialized_active_posts.append(post_data)

        return JsonResponse({'active_posts': serialized_active_posts})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)






#Filter blog posts by category
@csrf_exempt
def get_posts_by_category(request, category_id):
    if request.method == 'GET':
        try:
            # Find the category
            category = Category.objects.get(category_id=category_id)

            # Find all posts related to the category
            posts = BlogPost.objects.filter(category=category, status='active')

            # Serialize posts into JSON format
            serialized_posts = []
            for post in posts:
                post_data = {
                    'post_id': post.post_id,
                    'title': post.title,
                    'image': post.image.url if post.image else None,
                    'user': post.user.username,
                    'category': post.category.name,
                }
                serialized_posts.append(post_data)

            return JsonResponse({'posts': serialized_posts})
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)







#Filter blog posts by tag
@csrf_exempt
def get_posts_by_tag(request, tag_name):
    if request.method == 'GET':
        # Find all tags with the given name
        tags = Tag.objects.filter(name=tag_name)

        # Check if any tags were found
        if tags.exists():
            # Find all posts related to the tags
            posts = BlogPost.objects.filter(tag__in=tags, status='active')

            # Serialize posts into JSON format
            serialized_posts = []
            for post in posts:
                post_data = {
                    'title': post.title,
                    'image': post.image.url if post.image else None,
                    'user': post.user.username,
                    'category': post.category.name
                }
                serialized_posts.append(post_data)

            return JsonResponse({'posts': serialized_posts})
        else:
            return JsonResponse({'error': 'Tag not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)






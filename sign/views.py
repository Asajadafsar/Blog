from django.shortcuts import render
from django.http import HttpResponse
from .models import User
import hashlib
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required


#register user
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        
        # Check if required fields are present
        required_fields = ['username', 'password', 'email', 'phone_number']
        if all(field in data for field in required_fields):
            # Extract data
            username = data['username']
            password = data['password']
            email = data['email']
            phone_number = data['phone_number']

            # Check if the user already exists
            if User.objects.filter(username=username).exists():
                return HttpResponse('User already exists!', status=409)

            # Check if any field is empty
            if any(data[field] == '' for field in required_fields):
                return HttpResponse('One or more required fields are empty!', status=400)

            # Hash the password
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # Create the user
            user = User(username=username, password=hashed_password, email=email, phone_number=phone_number)
            user.save()

            return HttpResponse('User registered successfully!')
        else:
            return HttpResponse('Required fields are missing!', status=400)
    else:
        return HttpResponse('Method not allowed!', status=405)


#login user
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        
        # Check if required fields are present
        required_fields = ['username', 'password']
        if all(field in data for field in required_fields):
            # Extract data
            username = data['username']
            password = data['password']
            
            # Hash the provided password using the same hashing algorithm as during registration
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # Check if the user exists and password matches
            if User.objects.filter(username=username, password=hashed_password).exists():
                return HttpResponse('Login successful!')
            else:
                return HttpResponse('Invalid username or password!', status=401)
        else:
            return HttpResponse('Required fields are missing!', status=400)
    else:
        return HttpResponse('Method not allowed!', status=405)




# #edit user_profile
# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data!'}, status=400)
        
#         user = request.user
        
#         # Check if the fields are present in the request data
#         if 'email' in data:
#             user.email = data['email']
#         if 'phone_number' in data:
#             user.phone_number = data['phone_number']
        
#         # Save the changes to the user object
#         user.save()
        
#         return JsonResponse({'message': 'Profile updated successfully!'})
#     else:
#         return JsonResponse({'error': 'Method not allowed!'}, status=405)
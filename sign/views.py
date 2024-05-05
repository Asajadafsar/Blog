from django.shortcuts import render
from django.http import HttpResponse
from .models import User
import hashlib
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        #this body json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON data!', status=400)
        #check filed
        required_fields = ['username', 'password', 'email', 'phone_number']
        if all(field in data for field in required_fields):
            #export data
            username = data['username']
            password = data['password']
            email = data['email']
            phone_number = data['phone_number']

            #hash password
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            #query register
            user = User(username=username, password=hashed_password, email=email, phone_number=phone_number)
            user.save()

            return HttpResponse('User registered successfully!')
        else:
            #Not data this request
            return HttpResponse('Required fields are missing!', status=400)
    else:
        #request Post post
        return render(request, 'register.html')

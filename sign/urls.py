from django.urls import path
from .views import register_user, login_user,profile,edit_profile,reset_password

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('profile/', profile, name='profile'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('rest', reset_password, name='reset_password'),

]
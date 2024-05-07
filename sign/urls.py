from django.urls import path
from .views import register_user, login_user,profile,edit_profile,reset_password,add_post,edit_post,user_posts,delete_post,display_post

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('profile/', profile, name='profile'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('rest/', reset_password, name='reset_password'),
    path('add_post/', add_post, name='add_post'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('user_posts/', user_posts, name='user_posts'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('display_post/<int:post_id>/', display_post, name='display_post'),

]
from django.urls import path
from .views import get_users, add_user, delete_user, update_user,delete_admin_log,view_admin_logs,get_user,get_blog_posts
from .views import get_blog_post,delete_blog_post,update_blog_post



urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/<int:user_id>/', get_user, name='get_user'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/edit/<int:user_id>/', update_user, name='update_user'),
    path('logs/<int:log_id>/', delete_admin_log, name='delete_admin_log'),
    path('logs/', view_admin_logs, name='view_admin_logs'),
    path('posts/', get_blog_posts, name='get_blog_posts'),
    path('posts/<int:post_id>/', get_blog_post, name='get_blog_post'),
    path('posts/delete/<int:post_id>/', delete_blog_post, name='delete_blog_post'),
    path('posts/edit/<int:post_id>/', update_blog_post, name='update_blog_post'),



]

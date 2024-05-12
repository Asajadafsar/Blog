from django.urls import path
from .views import manage_users, manage_user, delete_admin_log,view_admin_logs,get_blog_posts
from .views import manage_blog_post,get_comments,manage_comment,get_tags,get_tag



urlpatterns = [
    path('users/', manage_users, name='manage_users'),
    path('users/<int:user_id>/', manage_user, name='manage_user'),
    path('users/', manage_users, name='manage_users'),
    path('users/<int:user_id>/', manage_user, name='manage_user'),
    path('users/<int:user_id>/', manage_user, name='manage_user'),
    path('logs/<int:log_id>/', delete_admin_log, name='delete_admin_log'),
    path('logs/', view_admin_logs, name='view_admin_logs'),
    path('posts/', get_blog_posts, name='get_blog_posts'),
    path('posts/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('posts/delete/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('posts/edit/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('comments/', get_comments, name='get_comments'),
    path('comments/<int:comment_id>/', manage_comment, name='manage_comment'),
    path('comments/<int:comment_id>/', manage_comment, name='manage_comment'),
    path('tags/', get_tags, name='get_tags'),
    path('tags/<int:tag_id>/', get_tag, name='get_tag'),


]

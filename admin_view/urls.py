from django.urls import path
from .views import manage_users, manage_user,get_blog_posts,manage_logs
from .views import manage_blog_post,get_comments,manage_comment,get_tags,get_tag,get_categories,manage_category



urlpatterns = [
    path('users', manage_users, name='get user_id'),
    path('users/', manage_users, name='view all'),
    path('users/<int:user_id>/', manage_user, name='delete and views'),
    path('users/<int:user_id>', manage_user, name='Update'),
    path('logs/', manage_logs, name='view_admin_logs'),
    path('logs/<int:log_id>', manage_logs, name='delete_admin_log'),
    path('posts/', get_blog_posts, name='get_blog_posts'),
    path('posts/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('posts/delete/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('posts/edit/<int:post_id>/', manage_blog_post, name='manage_blog_post'),
    path('comments/', get_comments, name='get_comments'),
    path('comments/<int:comment_id>/', manage_comment, name='manage_comment'),
    path('comments/<int:comment_id>/', manage_comment, name='manage_comment'),
    path('tags/', get_tags, name='get_tags'),
    path('tags/<int:tag_id>/', get_tag, name='get_tag'),
    path('category/', get_categories, name='get_categories'),
    path('category/<int:category_id>/', manage_category, name='manage_category'),
    path('category/', manage_category, name='manage_category'),


]

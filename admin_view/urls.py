from django.urls import path
from .views import manage_users, manage_user,manage_blog_posts,manage_logs,manage_blog_post
from .views import manage_comment,manage_tag,manage_categories,manage_category



urlpatterns = [
    path('users', manage_users, name='get user_id'),
    path('users/', manage_users, name='view all'),
    path('users/<int:user_id>/', manage_user, name='delete and views'),
    path('users/<int:user_id>', manage_user, name='Update'),
    path('logs/', manage_logs, name='view_admin_logs'),
    path('logs/<int:log_id>', manage_logs, name='delete_admin_log'),
    path('posts', manage_blog_posts, name='get'),
    path('posts/', manage_blog_posts, name='vew'),
    path('posts/<int:post_id>/', manage_blog_post, name='get'),
    path('posts/<int:post_id>', manage_blog_post, name='edit'),
    path('comment/', manage_comment, name='manage_comment'),
    path('comment/<int:comment_id>', manage_comment, name='manage_comment'),
    path('tag/', manage_tag, name='manage_tag'),
    path('tag/<int:tag_id>', manage_tag, name='manage_tag'),
    path('tag/<int:tag_id>/', manage_tag, name='manage_tag'),

    path('category/', manage_categories, name='manage_categories'),
    path('category', manage_categories, name='manage_categories'),
    path('category/<int:category_id>', manage_category, name='manage_category'),
    path('category/<int:category_id>/', manage_category, name='manage_category'),

]

from django.urls import path
from .views import register_user, login_user,profile,edit_profile,reset_password,add_post,edit_post,user_posts
from .views import add_comment,edit_comment,delete_post,display_post,delete_comment,add_deraf_post,edit_draft_post
from .views import publish_draft_post,unpublish_post,display_draft_posts,search_active_posts,get_posts_by_category
from .views import get_posts_by_tag,home



urlpatterns = [
    path('', home, name='home'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('rest/', reset_password, name='reset_password'),
    path('add_post/', add_post, name='add_post'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('user_posts/', user_posts, name='user_posts'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('display_post/<int:post_id>/', display_post, name='display_post'),
    path('add-comment/<int:post_id>/', add_comment, name='add_comment'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('add_deraf_post/', add_deraf_post, name='add_deraf_post'),
    path('edit_draft_post/<int:post_id>/', edit_draft_post, name='edit_draft_post'),
    path('publish_draft_post/<int:post_id>/', publish_draft_post, name='publish_draft_post'),
    path('unpublish_post/<int:post_id>/', unpublish_post, name='unpublish_post'),
    path('display_draft_posts/', display_draft_posts, name='display_draft_posts'),
    path('search_active_posts/', search_active_posts, name='search_active_posts'),
    path('get_posts_by_category/<int:category_id>/', get_posts_by_category, name='get_posts_by_category'),
    path('get_posts_by_tag/<str:tag_name>/', get_posts_by_tag, name='get_posts_by_tag'),

]
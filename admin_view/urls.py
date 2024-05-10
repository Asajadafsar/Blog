from django.urls import path
from .views import get_users, add_user, delete_user, update_user,delete_admin_log,view_admin_logs

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('logs/<int:log_id>/', delete_admin_log, name='delete_admin_log'),
    path('logs/', view_admin_logs, name='view_admin_logs'),



]

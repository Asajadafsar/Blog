
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sign/', include('sign.urls')), 
    path('admin_view/', include('admin_view.urls')), 

]
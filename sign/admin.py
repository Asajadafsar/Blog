from django.contrib import admin
from sign.models import User,Category,BlogPost,Comment

admin.site.register(User)
admin.site.register(Category)
admin.site.register(BlogPost)
admin.site.register(Comment)
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='user')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name








class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    blog_images = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return self.title



class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user_id.username} on '{self.post_id.title}'"



class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    post_id = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return self.name
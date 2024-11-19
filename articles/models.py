from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# class Article(models.Model):
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     views = models.IntegerField(default=0)
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
#     image = models.ImageField(blank=True, null=True,upload_to='images/')
#     # likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
#     # dislikes = models.ManyToManyField(User, related_name='disliked_articles', blank=True)

#     def __str__(self):
#         return self.title

#     def increase_views(self):
#         self.views += 1
#         self.save(update_fields=['views'])

#     # def total_likes(self):
#     #     return self.likes.count()

#     # def total_dislikes(self):
#     #     return self.dislikes.count()

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_articles', blank=True)
    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'Comment by {self.author} on {self.article}'
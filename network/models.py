from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    def __str__(self) -> str:
        return f'{self.username}'
    
    
class Post(models.Model):
    class Meta:
        ordering = ['-creation_date']
        
    creator = models.ForeignKey('User', related_name = 'created_posts', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add= True)
    text_content = models.TextField(max_length=500, null=False, blank=False)
    liked_by  = models.ManyToManyField('User', through='Liked')
    edited = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Post content: {self.text_content}'


#through table for users liking posts
class Liked(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','target_post'],  name="unique_liking")
        ]
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    target_post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user} likes {self.target_post}'



#intermediary table for users following other users
class Followed(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['following','followers'],  name="unique_following")
        ]

    following= models.ForeignKey('User', related_name='following', on_delete=models.CASCADE)
    followers = models.ForeignKey('User',related_name='followers',on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.following} follows {self.followers}'



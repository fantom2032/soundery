from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class Track(models.Model):
    title = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='tracks/')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_tracks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "track") 



class Comment(models.Model):
    track = models.ForeignKey('Track', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tracks = models.ManyToManyField(Track, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
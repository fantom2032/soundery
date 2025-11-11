import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Track, Album

@receiver(post_delete, sender=Track)
def delete_track_files(sender, instance, **kwargs):
    if instance.audio_file and os.path.isfile(instance.audio_file.path):
        os.remove(instance.audio_file.path)

    if instance.cover and os.path.isfile(instance.cover.path):
        same_cover_used = Track.objects.filter(
            cover=instance.cover.name
        ).exclude(id=instance.id).exists()

        if not same_cover_used:
            os.remove(instance.cover.path)


@receiver(post_delete, sender=Album)
def delete_album_cover(sender, instance, **kwargs):
    if instance.cover and os.path.isfile(instance.cover.path):
        same_cover_used = Track.objects.filter(
            cover=instance.cover.name
        ).exists()
        if not same_cover_used:
            os.remove(instance.cover.path)
from django.core.exceptions import ValidationError
from django.db import models

from wandlung.storages import MediaStorage


class YouTubeVideo(models.Model):
    video_id = models.CharField(max_length=20, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    duration = models.DurationField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    original_video = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title

    def signed_thumbnail_url(self):
        if not self.thumbnail:
            return None

        return MediaStorage().url(self.thumbnail.name)


VIDEO_HEIGHT_CHOICES = [
    (240, '240p'),
    (360, '360p'),
    (480, '480p'),
    (720, '720p'),
    (1080, '1080p'),
]

class Settings(models.Model):
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    anthropic_api_key = models.CharField(max_length=255, blank=True, null=True)
    max_video_height = models.IntegerField(default=720, choices=VIDEO_HEIGHT_CHOICES)
    use_he_aac_v2 = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValidationError('There can be only one Settings instance')
        super().save(*args, **kwargs)


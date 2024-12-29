from django.core.exceptions import ValidationError
from django.db import models

from wandlung.storages import MediaStorage


class YouTubeVideo(models.Model):
    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    video_id = models.CharField(max_length=20, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    duration = models.DurationField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    original_video = models.FileField(upload_to='videos/')
    audio = models.FileField(upload_to='audios/')

    def __str__(self):
        return self.title

    def signed_thumbnail_url(self):
        if not self.thumbnail:
            return None

        return MediaStorage().url(self.thumbnail.name)


class Subtitle(models.Model):
    class Meta:
        verbose_name = 'Subtitle'
        verbose_name_plural = 'Subtitles'
        unique_together = ('video', 'language',)

    video = models.ForeignKey(YouTubeVideo, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=32)
    is_transcribed = models.BooleanField(default=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


VIDEO_HEIGHT_CHOICES = [
    (240, '240p'),
    (360, '360p'),
    (480, '480p'),
    (720, '720p'),
    (1080, '1080p'),
]

class Settings(models.Model):
    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'

    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    anthropic_api_key = models.CharField(max_length=255, blank=True, null=True)
    max_video_height = models.IntegerField(default=720, choices=VIDEO_HEIGHT_CHOICES)
    use_he_aac_v2 = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValidationError('There can be only one Settings instance')
        super().save(*args, **kwargs)


from django.db import models


class YouTubeVideo(models.Model):
    video_id = models.CharField(max_length=20, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', max_length=180)
    duration = models.DurationField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    original_video = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title


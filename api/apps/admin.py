from django.contrib import admin
from .models import YouTubeVideo, Subtitle, Settings


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_id', 'duration', 'width', 'height')
    search_fields = ('title', 'video_id')
    readonly_fields = ('video_id', 'width', 'height', 'duration')
    list_filter = ('height', 'width')


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('video', 'language', 'is_transcribed', 'created')


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('max_video_height', 'use_he_aac_v2')

    def has_add_permission(self, request):
        # Prevent creating multiple Settings instances
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the Settings instance
        return False

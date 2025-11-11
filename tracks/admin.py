from django.contrib import admin
from .models import Album, Track, Comment

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'created_at')
    search_fields = ('title', 'artist__username')
    list_filter = ('created_at',)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'album', 'created_at')
    search_fields = ('title', 'uploaded_by__username')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'created_at', 'parent')
    search_fields = ('user__username', 'album__title')
    list_filter = ('created_at',)

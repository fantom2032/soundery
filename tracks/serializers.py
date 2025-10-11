from rest_framework import serializers
from .models import Track, Like, Comment, Favorite

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at"]


class TrackSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = ["id", "title", "audio_file", "cover_image", "author", "likes_count", "comments", "created_at"]

    def get_likes_count(self, obj):
        return obj.likes.count()
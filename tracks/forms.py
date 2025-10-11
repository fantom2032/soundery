from django import forms
from .models import Track, Comment, Playlist

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["title", "audio_file", "cover"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'tracks']
        widgets = {
            'tracks': forms.CheckboxSelectMultiple
        }
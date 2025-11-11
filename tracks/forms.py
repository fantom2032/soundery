from django import forms
from .models import Track, Comment, Playlist, Album , Report

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'cover', 'genre']

class TrackInAlbumForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'audio_file']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Напишите комментарий...',
            'rows': 3,
            'style': 'width:100%; resize:none; border-radius:10px; padding:8px;'
        }),
        required=False
    )
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description']
class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['title', 'description', 'cover', 'genre']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Опишите проблему...',
                'rows': 4,
                'style': 'width:100%; resize:none; border-radius:10px; padding:8px;'
            })
        }

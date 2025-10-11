from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from tracks.models import Track, Playlist
from django.contrib.auth import get_user_model

User = get_user_model()
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile")
    else:
        form = CustomAuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")




def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_tracks = Track.objects.filter(user=user)
    user_playlists = Playlist.objects.filter(user=user)
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'user_tracks': user_tracks,
        'user_playlists': user_playlists,
    })
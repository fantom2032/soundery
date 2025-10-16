from django.urls import path
from . import views
from .views import register_view, login_view, logout_view, profile_view

urlpatterns = [
     path('profile/<str:username>/', views.profile_view, name='profile'),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
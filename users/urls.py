from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("complete-profile/", views.profile_setup, name="profile_setup"),
    path("profile/refresh-cv/", views.refresh_cv_data, name="refresh_cv_data"),
    path("upload-cv/", views.cv_upload, name="cv_upload"),
    path("login/", views.CVRequiredLoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

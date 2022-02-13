from django.urls import path
from identity.views import RegisterView, ProfileView


app_name = "api"
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile')
]


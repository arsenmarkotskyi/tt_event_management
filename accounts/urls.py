from django.urls import path
from .views import (
    UserRegistrationView,
    login_view,
    logout_view,
    user_profile
)

app_name = 'accounts'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', user_profile, name='profile'),
]


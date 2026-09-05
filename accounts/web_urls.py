from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_web_view

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_web_view, name='web_register'),
]


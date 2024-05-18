from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from renamer import views


urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('config_form/', views.config_form, name='config_form'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(template_name='renamer/logout.html'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='renamer/login.html'), name='login'),
]

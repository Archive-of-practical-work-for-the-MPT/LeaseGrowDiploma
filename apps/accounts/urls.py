from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('backup/', views.backup_view, name='backup'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dash', views.dash, name='dash'),
    path('delete_project/<str:pk>/', views.deleteProject, name="delete_project"),
]
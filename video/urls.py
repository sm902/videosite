from . import views
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('video/', views.movie, name='video'),
]

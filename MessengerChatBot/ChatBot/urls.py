from django import views
from django.urls import path, re_path
from .import views
from .views import (
     FacebookWebhookView,
)

app_name = 'ChatBot'

urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^b89aadc35ee02bbd607e9ce77c40f3d2f73a9e5477919fc8dee732ca6452/$', FacebookWebhookView.as_view, name='webhook'),
]

from django.urls import path
from file import views

urlpatterns = [
    path('upload', views.upload_file),
    path('all', views.all_file),
    path('delete', views.delete_file),
    path('update', views.update_file),
]
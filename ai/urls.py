from django.urls import path
from ai import views

urlpatterns = [
    path('polish', views.polish),
    path('continue', views.continuation),

]
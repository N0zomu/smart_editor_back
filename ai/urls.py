from django.urls import path
from ai import views

urlpatterns = [
    path('polish', views.polish),
    path('mindMap', views.mindmap),
    path('typeset', views.typeset),
    path('ocr', views.get_ocr),

]
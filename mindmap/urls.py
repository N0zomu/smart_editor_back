from django.urls import path
from mindmap import views

urlpatterns = [
    path('has', views.get_mindmap),
    path('store', views.store_mindmap),

]
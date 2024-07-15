from django.urls import path
from user import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('selfInfo', views.self_info),
    path('changeName', views.change_nickname),
    path('changePassword',views.change_password),
    path('changeIcon', views.change_icon),
    path('icon', views.get_icon),
    path('info', views.user_info),
    path('searchEmail', views.user_email_search),
    path('searchName', views.user_name_search),
    path('upgrade', views.upgrade),
]
from django.urls import path
from message import views

urlpatterns = [
    path('create', views.create_message),
    path('all', views.all_messages),
    path('operate', views.change_message),
    path('delete', views.delete_message),
    # path('operate_all', views.change_all),
    path('self/<int:msg_id>', views.message_info),
]
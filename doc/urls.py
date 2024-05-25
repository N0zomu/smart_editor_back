from django.urls import path
from doc import views

urlpatterns = [
    path('createDoc', views.create_doc),
    path('deleteDoc', views.delete_doc),
    path('regainDoc', views.regain_doc),
    path('path', views.get_path),
    path('root', views.root_doc),
    path('folder', views.folder_doc),
    path('teamRoot', views.team_root_doc),
    path('move', views.move_doc),
    path('teamDelete', views.team_doc_delete),
    path('teamRegain', views.team_doc_regain),
]
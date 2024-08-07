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
    path('collect',views.add_collect),
    path('removeCollect', views.remove_collect),
    path('updateDoc', views.update_doc),
    path('docContent', views.doc_content),
    path('allCollection', views.get_collection),
    path('recent', views.get_recent),
    path('getDelete', views.get_delete),
    path('completeDelete', views.delete_c_doc),
    path('deleteAll', views.delete_all),
    path('getFolderTeam', views.get_folder_team),
    path('search', views.search),
]
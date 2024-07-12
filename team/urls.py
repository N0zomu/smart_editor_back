from django.urls import path
from team import views

urlpatterns = [
    path('all', views.all_team),
    path('create', views.create_team),
    path('add', views.add_member),
    path('quit', views.quit_member),
    path('allMember', views.see_members),
    path('info/<int:team_id>', views.team_info),
    path('delete', views.delete_team),
    path('regain', views.regain_team),
    path('search', views.search_team),
    path('quitSelf', views.quit_team),

]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("stats/ranking_table", views.ranking_table, name="ranking_table"),
    path("stats/fixtures_list", views.fixtures_list, name="fixtures_list"),
]

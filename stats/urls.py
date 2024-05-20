from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("stats/ranking_table", views.ranking_table, name="ranking_table"),
]

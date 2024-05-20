from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("stats/rankings", views.ranking_table, name="rankings"),
]

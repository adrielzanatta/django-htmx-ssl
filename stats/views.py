from django.shortcuts import render
from stats.models import SeasonPlayerStatistics, Fixture


# Create your views here.
def index(request):
    return render(request, "home.html")


def ranking_table(request):
    players = SeasonPlayerStatistics.objects.all()

    context = {"players": players}

    return render(request, "rankings.html", context)


def fixtures_list(request):
    fixtures = Fixture.objects.all()

    context = {"fixtures": fixtures}

    return render(request, "fixtures_list.html", context)

from django.shortcuts import render
from stats.models import SeasonPlayerStatistics


# Create your views here.
def index(request):
    if request.htmx:
        template = "partials/home_content.html"
    else:
        template = "content.html"

    return render(request, template)


def ranking_table(request):
    players = SeasonPlayerStatistics.objects.all()
    context = {"players": players}

    if request.htmx:
        template = "partials/ranking_table.html"
    else:
        template = "content.html"

    return render(request, template, context)

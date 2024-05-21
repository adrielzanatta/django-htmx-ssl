from django.shortcuts import render
from django.db.models import Prefetch
from stats.models import SeasonPlayerStatistics, Fixture, Season, FixturePlayerStatistics, Team


# Create your views here.
def season_filter(request):
    season_selected_id = request.GET.get("filter_season")
    seasons = Season.objects.all()

    if season_selected_id:
        season_selected = seasons.get(id=season_selected_id)
    else:
        season_selected = seasons.first()

    return season_selected, seasons


def index(request):
    season_selected, seasons = season_filter(request)

    context = {
        "seasons": seasons,
        "season_selected": season_selected,
    }
    if request.htmx:
        template = "partials/home_content.html"
    else:
        template = "content.html"

    return render(request, template, context)


def ranking_table(request):
    season_selected, seasons = season_filter(request)

    players = SeasonPlayerStatistics.objects.filter(season=season_selected).select_related("player")

    context = {
        "players": players,
        "seasons": seasons,
        "season_selected": season_selected,
    }

    if request.htmx:
        template = "partials/ranking_table.html"
    else:
        template = "content.html"

    return render(request, template, context)


def fixtures_list(request):
    season_selected, seasons = season_filter(request)

    fixtures = (
        Fixture.objects.select_related("season", "drafter")
        .prefetch_related(
            Prefetch(
                "players_stats",
                queryset=FixturePlayerStatistics.objects.select_related("player", "team"),
            )
        )
        .filter(season=season_selected)
    )

    context = {
        "fixtures": fixtures,
        "teams": Team.SIDE_CHOICES,
        "seasons": seasons,
        "season_selected": season_selected,
    }

    if request.htmx:
        template = "partials/fixtures_list.html"
    else:
        template = "content.html"

    return render(request, template, context)

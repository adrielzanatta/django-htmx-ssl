from django.contrib import admin
from stats.models import Player, Fixture, FixturePlayerStatistics, SeasonPlayerStatistics, Season, Team

# Register your models here.


# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(FixturePlayerStatistics)
class FixturePlayerStatisticsAdmin(admin.ModelAdmin):
    pass


@admin.register(SeasonPlayerStatistics)
class SeasonPlayerStatisticsAdmin(admin.ModelAdmin):
    pass


class FixturePlayerStatisticsInLine(admin.TabularInline):
    model = FixturePlayerStatistics


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    inlines = [
        FixturePlayerStatisticsInLine,
    ]

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
    inlines = [FixturePlayerStatisticsInLine]

    def save_model(self, request, obj, form, change):
        # Save the fixture first
        super().save_model(request, obj, form, change)

        # Now call the methods to calculate points and update statistics
        obj.calculate_points_fixture_player_statistics()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # Ensure fixture is saved again to update related stats properly
        form.instance.save()

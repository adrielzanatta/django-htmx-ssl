from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Count, Case, When, Avg, IntegerField
from stats.models import Fixture, SeasonPlayerStatistics, FixturePlayerStatistics


@receiver(post_save, sender=Fixture)
@receiver(post_delete, sender=Fixture)
def fixture_count_changed(sender, instance, **kwargs):
    fixture_player_statistics = FixturePlayerStatistics.objects.all()

    for p in fixture_player_statistics:
        season_player_stats = FixturePlayerStatistics.objects.filter(
            fixture__season=p.fixture.season, player=p.player
        ).aggregate(
            count_matches_played=Count("id"),
            sum_goals_scored=Sum("goals_scored"),
            sum_mvp_votes_received=Sum("mvp_votes_received"),
            count_mvp=Sum(Case(When(mvp=True, then=1), output_field=IntegerField()), default=0),
            sum_points=Sum("points"),
            count_wins=Sum(Case(When(points=3, then=1), output_field=IntegerField()), default=0),
            count_losses=Sum(Case(When(points=0, then=1), output_field=IntegerField()), default=0),
            count_draws=Sum(Case(When(points=1, then=1), output_field=IntegerField()), default=0),
            avg_goals=Avg("goals_scored"),
        )

        stats = season_player_stats

        season_player_instance, _ = SeasonPlayerStatistics.objects.get_or_create(
            season=instance.season, player=p.player
        )

        season_player_instance.matches_played = stats["count_matches_played"]
        season_player_instance.goals_scored = stats["sum_goals_scored"]
        season_player_instance.mvp_votes_received = stats["sum_mvp_votes_received"]
        season_player_instance.mvp_count = stats["count_mvp"]
        season_player_instance.points_earned = stats["sum_points"]
        season_player_instance.wins = stats["count_wins"]
        season_player_instance.losses = stats["count_losses"]
        season_player_instance.draws = stats["count_draws"]
        season_player_instance.avg_goals = stats["avg_goals"]
        season_player_instance.points_pct = (
            season_player_instance.points_earned / (season_player_instance.matches_played * 3) * 100
        )

        season_player_instance.save()

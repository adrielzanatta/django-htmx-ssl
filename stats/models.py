from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Sum, Count, Case, When, IntegerField, Avg
from django.db.models.functions import Now


class User(AbstractBaseUser):
    pass


class Season(models.Model):
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return str(self.year)


class Player(models.Model):
    name = models.CharField(max_length=200)
    nickname = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Team(models.Model):
    SIDE_CHOICES = [
        (1, "Team A"),
        (2, "Team B"),
    ]
    side_name = models.IntegerField(choices=SIDE_CHOICES, default="0")

    def __str__(self) -> str:
        return str(self.side_name)


class Fixture(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="fixtures")
    drafter = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="drafted_fixtures")
    date = models.DateField(default=Now())
    round_number = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Season: {self.season} - Round: {self.round_number}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.round_number = self.get_round_number()
        super().save(*args, **kwargs)
        self.calculate_points_fixture_player_statistics()
        self.update_season_players_statistics()

    def get_round_number(self):
        return self.season.fixtures.count() + 1

    @property
    def team_goals(self):
        teams = (
            FixturePlayerStatistics.objects.filter(fixture=self)
            .values("team__side_name")
            .annotate(total_goals=models.Sum("goals_scored"))
        )
        print({team["team__side_name"]: team["total_goals"] for team in teams})
        return {team["team__side_name"]: team["total_goals"] for team in teams}

    @property
    def difference_goals(self):
        team_goals = self.team_goals
        print(team_goals)
        team_1_goals = team_goals.get(1, 0)
        team_2_goals = team_goals.get(2, 0)

        return team_1_goals - team_2_goals

    @property
    def winner_team(self):
        diff = self.difference_goals
        if diff == 0:
            return None
        elif diff > 0:
            return 1
        else:
            return 2

    def calculate_points_fixture_player_statistics(self):
        winner_team = self.winner_team
        players_stats = FixturePlayerStatistics.objects.filter(fixture=self.pk)

        for player in players_stats:
            if winner_team is None:
                player.points = 1
            elif player.team.side_name == winner_team:
                player.points = 3
            else:
                player.points = 0
            player.save()

    def update_season_players_statistics(self):
        fixture_player_statistics = FixturePlayerStatistics.objects.filter(fixture=self.pk)

        for p in fixture_player_statistics:
            season_player_stats = FixturePlayerStatistics.objects.filter(
                fixture__season=self.season, player=p.player
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
                season=self.season, player=p.player
            )

            ins = season_player_instance
            ins.matches_played = stats["count_matches_played"]
            ins.goals_scored = stats["sum_goals_scored"]
            ins.mvp_votes_received = stats["sum_mvp_votes_received"]
            ins.mvp_count = stats["count_mvp"]
            ins.points_earned = stats["sum_points"]
            ins.wins = stats["count_wins"]
            ins.losses = stats["count_losses"]
            ins.draws = stats["count_draws"]
            ins.avg_goals = stats["avg_goals"]
            ins.points_pct = ins.points_earned / (ins.matches_played * 3) * 100

            ins.save()


class FixturePlayerStatistics(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name="players_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="fixtures_stats")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="teams_stats")
    goals_scored = models.PositiveSmallIntegerField(default=0)
    mvp_votes_received = models.PositiveSmallIntegerField(default=0)
    mvp = models.BooleanField(default=False)
    points = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("fixture", "player")

    def save(self, *args, **kwargs):
        self.is_mvp()
        super().save(*args, **kwargs)

    def is_mvp(self):
        MVP_TRESHOLD = 3
        self.mvp = self.mvp_votes_received >= MVP_TRESHOLD

    def __str__(self) -> str:
        return f"{self.fixture} - Player: {self.player.name}"


class SeasonPlayerStatistics(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="players_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="season_stats")
    matches_played = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    goals_scored = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    mvp_votes_received = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    mvp_count = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    points_earned = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    wins = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    losses = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    draws = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    avg_goals = models.FloatField(default=0, blank=True, null=True)
    points_pct = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        unique_together = ("player", "season")

    def __str__(self) -> str:
        return f"Season: {self.season.year} - Player: {self.player.name}"

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

MVP_TRESHOLD = 3


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
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class Fixture(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="fixtures")
    drafter = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="drafted_fixtures")
    right_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="right_team_fixtures")
    left_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="left_team_fixtures")
    date = models.DateField()
    round_number = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Season: {self.season} - Round: {self.round_number} - "

    def save(self, *args, **kwargs):
        if not self.pk:
            self.round_number = self.get_round_number()
        super().save(*args, **kwargs)

    def get_round_number(self):
        return self.season.fixtures.count() + 1

    @property
    def right_team_goals(self):
        goals_scored = FixturePlayerStatistics.objects.filter(team=self.right_team).aggregate(
            total_goals=models.Sum("goals_scored")
        )["total_goals"]

        return goals_scored if goals_scored is not None else 0

    @property
    def left_team_goals(self):
        goals_scored = FixturePlayerStatistics.objects.filter(team=self.left_team).aggregate(
            total_goals=models.Sum("goals_scored")
        )["total_goals"]

        return goals_scored if goals_scored is not None else 0

    @property
    def difference_goals(self):
        return self.left_team_goals - self.right_team_goals

    @property
    def winner_team(self):
        diff = self.difference_goals
        if diff == 0:
            return None
        elif diff > 0:
            return self.left_team
        else:
            return self.right_team


class FixturePlayerStatistics(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name="players_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="fixtures_stats")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="teams_stats")
    goals_scored = models.PositiveSmallIntegerField(default=0)
    mvp_votes_received = models.PositiveSmallIntegerField(default=0)
    mvp = models.BooleanField(default=False)

    class Meta:
        unique_together = ("fixture", "player")

    def save(self, *args, **kwargs):
        self.is_mvp()
        super().save(*args, **kwargs)
        self.update_player_season_statistics()

    def is_mvp(self):
        self.mvp = self.mvp_votes_received >= MVP_TRESHOLD

    def update_player_season_statistics(self):
        points = self.calculate_points

        player_season_stats, _ = SeasonPlayerStatistics.objects.get_or_create(
            player=self.player, season=self.fixture.season
        )

        player_season_stats.matches_played += 1
        player_season_stats.goals_scored += self.goals_scored
        player_season_stats.mvp_votes_received += self.mvp_votes_received
        player_season_stats.mvp_count += self.mvp
        player_season_stats.points_earned += points

        if points == 3:
            player_season_stats.wins += 1
        elif points == 0:
            player_season_stats.loses += 1
        else:
            player_season_stats.draws += 1

        player_season_stats.save()

    @property
    def calculate_points(self):
        winner_team = self.fixture.winner_team
        if winner_team is None:
            return 1
        elif self.team == winner_team:
            return 3
        else:
            return 0


class SeasonPlayerStatistics(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="players_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="season_stats")
    matches_played = models.PositiveSmallIntegerField(default=0)
    goals_scored = models.PositiveSmallIntegerField(default=0)
    mvp_votes_received = models.PositiveSmallIntegerField(default=0)
    mvp_count = models.PositiveSmallIntegerField(default=0)
    points_earned = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    loses = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("player", "season")

    def __str__(self) -> str:
        return f"Season: {self.season.year} - Player: {self.player.name}"

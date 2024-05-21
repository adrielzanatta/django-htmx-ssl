from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
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
        return self.nickname


class Fixture(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="fixtures")
    drafter = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="drafted_fixtures")
    date = models.DateField(default=Now())
    round_number = models.PositiveSmallIntegerField(blank=True, null=True)
    goal_balance = models.SmallIntegerField(blank=True, null=True)
    winner_team = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Season: {self.season} - Round: {self.round_number}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.round_number = self.get_round_number()
        self.set_team_goals_scored()
        self.set_goal_balance()
        self.set_winner_team()
        self.calculate_points_fixture_player_statistics()
        super(Fixture, self).save(*args, **kwargs)

    def get_round_number(self):
        return self.season.fixtures.count() + 1

    def get_team_goals_scored(self):
        teams_goals_scored = (
            FixturePlayerStatistics.objects.filter(fixture=self.pk)
            .values("team__side_name")
            .annotate(total_goals=models.Sum("goals_scored"))
        )

        return {team["team__side_name"]: team["total_goals"] for team in teams_goals_scored}

    def set_team_goals_scored(self):
        teams_goals = self.get_team_goals_scored()

        teams = Team.objects.filter(fixture=self.pk)

        for team in teams:
            team.goals_scored = teams_goals[team.side_name]
            team.save()

    def set_goal_balance(self):
        teams_goals_scored = Team.objects.filter(fixture=self.pk)

        team_1_goals_scored = teams_goals_scored.get(side_name=1)
        team_2_goals_scored = teams_goals_scored.get(side_name=2)

        return team_1_goals_scored - team_2_goals_scored

    def set_winner_team(self):
        diff = self.goal_balance
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


class Team(models.Model):
    SIDE_CHOICES = (
        (1, "Team A"),
        (2, "Team B"),
    )

    side_name = models.IntegerField(choices=SIDE_CHOICES, default="0")
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name="teams")
    goals_scored = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.side_name)


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
        super(FixturePlayerStatistics, self).save(*args, **kwargs)

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

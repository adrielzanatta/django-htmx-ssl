from django.test import TestCase
from .models import Season, Player, Team, Fixture, FixturePlayerStatistics, SeasonPlayerStatistics


class ModelsTestCase(TestCase):
    def setUp(self):
        self.season = Season.objects.create(year=2022, start_date="2022-01-01", end_date="2022-12-31")
        self.player1 = Player.objects.create(name="John Doe", nickname="JD")
        self.player2 = Player.objects.create(name="Jane Smith", nickname="JS")
        self.team1 = Team.objects.create(side_name=1)
        self.team2 = Team.objects.create(side_name=2)
        self.fixture = Fixture.objects.create(season=self.season, drafter=self.player1, date="2022-01-15")

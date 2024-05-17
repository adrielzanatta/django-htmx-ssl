from django.test import TestCase
from .models import Season, Player, Team, Fixture, FixturePlayerStatistics, SeasonPlayerStatistics


class TestModels(TestCase):
    def setUp(self):
        # create season
        self.season1 = Season.objects.create(
            year=2024,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # create players
        self.player1 = Player.objects.create(name="Adriel", nickname="adrilol")
        self.player2 = Player.objects.create(name="Alana", nickname="alana")
        self.player3 = Player.objects.create(name="Joseli", nickname="joce")

        # create teams
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")

        # create fixtures
        self.fixture1 = Fixture.objects.create(
            season=self.season1,
            drafter=self.player1,
            right_team=self.team1,
            left_team=self.team2,
            date="2024-05-16",
        )

        self.fixture2 = Fixture.objects.create(
            season=self.season1,
            drafter=self.player2,
            right_team=self.team1,
            left_team=self.team2,
            date="2024-05-17",
        )

        # create fixture players stats
        self.fixt_player11 = FixturePlayerStatistics.objects.create(
            fixture=self.fixture1, player=self.player1, team=self.team1, goals_scored=1, mvp_votes_received=3
        )

        self.fixt_player12 = FixturePlayerStatistics.objects.create(
            fixture=self.fixture1, player=self.player2, team=self.team1, goals_scored=2, mvp_votes_received=1
        )

        self.fixt_player13 = FixturePlayerStatistics.objects.create(
            fixture=self.fixture1, player=self.player3, team=self.team2, goals_scored=2
        )

        self.fixt_player21 = FixturePlayerStatistics.objects.create(
            fixture=self.fixture2, player=self.player1, team=self.team1, goals_scored=2, mvp_votes_received=4
        )

    # Fixture tests
    def test_round_number_on_creation(self):
        self.assertEquals(self.fixture1.round_number, 1)
        self.assertEquals(self.fixture2.round_number, 2)

    def test_properties_winner_team(self):
        self.assertEquals(self.fixture1.winner_team, self.team1)

    # Fixture Player Statistics tests
    def test_is_mvp_fixture_player_statistics(self):
        self.assertTrue(self.fixt_player11.mvp)
        self.assertFalse(self.fixt_player12.mvp)

    def test_fixture_player_statistics_calculate_points(self):
        self.assertEquals(self.fixt_player11.calculate_points, 3)
        self.assertEquals(self.fixt_player13.calculate_points, 0)

    def test_update_player_season_statistics(self):
        player1 = SeasonPlayerStatistics.objects.get(player=self.player1)
        player3 = SeasonPlayerStatistics.objects.get(player=self.player3)
        self.assertEquals(player1.goals_scored, 3)
        self.assertEquals(player1.mvp_count, 2)
        self.assertEquals(player1.matches_played, 2)
        self.assertEquals(player1.mvp_votes_received, 7)
        self.assertEquals(player1.points_earned, 6)
        self.assertEquals(player3.points_earned, 0)
        self.assertEquals(player1.wins, 2)
        self.assertEquals(player3.loses, 0)

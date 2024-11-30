# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import Game, Cup, RankAllTime
from django.db.models import Q


class Command(BaseCommand):
    help = _("Update medals table")

    def handle(self, *args, **options):
        flows = [1, 2]
        for flow in flows:
            all_cups_edition = Cup.objects.filter(c_flow=flow)
            all_games = Game.objects.filter(c_id__in=all_cups_edition)
            RankAllTime.objects.filter(c_flow=flow).delete()
            for game in all_games:
                if game.goals_away is None or game.goals_home is None:
                    continue
                # home team update
                team_data = RankAllTime.objects.filter(
                    t_id=game.t_id_h, c_flow=flow
                ).first()
                # init data first time for a team
                if not team_data:
                    team_data = RankAllTime()
                    team_data.loose = 0
                    team_data.wins = 0
                    team_data.draw = 0
                    team_data.games = 1
                    team_data.t_id = game.t_id_h
                    team_data.c_flow = flow
                    team_data.gdif = int(game.goals_home) - int(game.goals_away)
                    team_data.gscored = int(game.goals_home)
                    team_data.grecieved = int(game.goals_away)
                    team_data.points = game.home_points()
                    status = game.home_status()
                    if status == _("win"):
                        team_data.wins = 1
                    elif status == _("draw"):
                        team_data.draw = 1
                    elif status == _("loss"):
                        team_data.loose = 1
                    team_data.save()
                else:
                    team_data.gdif = (
                        team_data.gdif + int(game.goals_home) - int(game.goals_away)
                    )
                    team_data.games = team_data.games + 1
                    team_data.gscored = team_data.gscored + int(game.goals_home)
                    team_data.grecieved = team_data.grecieved + int(game.goals_away)
                    team_data.points = team_data.points + game.home_points()
                    status = game.home_status()
                    if status == _("win"):
                        team_data.wins = team_data.wins + 1
                    elif status == _("draw"):
                        team_data.draw = team_data.draw + 1
                    elif status == _("loss"):
                        team_data.loose = team_data.loose + 1
                    team_data.save()

                team_data = RankAllTime.objects.filter(
                    t_id=game.t_id_v, c_flow=flow
                ).first()
                # init data first time for a team
                if not team_data:
                    team_data = RankAllTime()
                    team_data.loose = 0
                    team_data.wins = 0
                    team_data.draw = 0
                    team_data.games = 1
                    team_data.t_id = game.t_id_v
                    team_data.c_flow = flow
                    team_data.gdif = int(game.goals_away) - int(game.goals_home)
                    team_data.gscored = int(game.goals_away)
                    team_data.grecieved = int(game.goals_home)
                    team_data.points = game.away_points()
                    status = game.away_status()
                    if status == _("win"):
                        team_data.wins = 1
                    elif status == _("draw"):
                        team_data.draw = 1
                    elif status == _("loss"):
                        team_data.loose = 1
                    team_data.save()
                else:
                    team_data.gdif = (
                        team_data.gdif + int(game.goals_away) - int(game.goals_home)
                    )
                    team_data.games = team_data.games + 1
                    team_data.gscored = team_data.gscored + int(game.goals_away)
                    team_data.grecieved = team_data.grecieved + int(game.goals_home)
                    team_data.points = team_data.points + game.away_points()
                    status = game.away_status()
                    if status == _("win"):
                        team_data.wins = team_data.wins + 1
                    elif status == _("draw"):
                        team_data.draw = team_data.draw + 1
                    elif status == _("loss"):
                        team_data.loose = team_data.loose + 1
                    team_data.save()

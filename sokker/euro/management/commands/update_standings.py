# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import Game, Cup, RankGroups


class Command(BaseCommand):
    help = _("Update medals table")

    def handle(self, *args, **options):
        all_cups_active = Cup.objects.filter(c_active=True)
        for cup in all_cups_active:
            print(cup.c_groups)
            for i in range(1, cup.c_groups + 1):
                print("get games for group:", i)
                all_games = Game.objects.filter(c_id=cup, group_id=i)
                RankGroups.objects.filter(c_id=cup, g_id=i).delete()
                for game in all_games:
                    if not game.goals_away or not game.goals_home:
                        continue
                    print(game)
                    # home team update
                    team_data = RankGroups.objects.filter(
                        t_id=game.t_id_h, c_id=cup, g_id=i
                    ).first()

                    # init data first time for a team
                    if not team_data:
                        team_data = RankGroups()
                        team_data.loose = 0
                        team_data.wins = 0
                        team_data.draw = 0
                        team_data.games = 1
                        team_data.c_id = cup
                        team_data.g_id = i
                        team_data.t_id = game.t_id_h
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
                        team_data.c_id = cup
                        team_data.g_id = i
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

                    team_data = RankGroups.objects.filter(
                        t_id=game.t_id_v, c_id=cup, g_id=i
                    ).first()
                    # init data first time for a team
                    if not team_data:
                        team_data = RankGroups()
                        team_data.c_id = cup
                        team_data.g_id = i
                        team_data.loose = 0
                        team_data.wins = 0
                        team_data.draw = 0
                        team_data.games = 1
                        team_data.t_id = game.t_id_v
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
                        team_data.c_id = cup
                        team_data.g_id = i
                        team_data.games = team_data.games + 1
                        team_data.gscored = team_data.gscored + int(game.goals_away)
                        team_data.grecieved = team_data.grecieved + int(game.goals_away)
                        team_data.points = team_data.points + game.away_points()
                        status = game.away_status()
                        if status == _("win"):
                            team_data.wins = team_data.wins + 1
                        elif status == _("draw"):
                            team_data.draw = team_data.draw + 1
                        elif status == _("loss"):
                            team_data.loose = team_data.loose + 1
                        team_data.save()

# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import Game, Cup, RankGroups


class Command(BaseCommand):
    help = _("Update arcades classification tables")

    def add_arguments(self, parser):
        parser.add_argument(
            '--cup-id',
            type=int,
            help=_('ID of the specific cup to update. If not provided, updates all active cups.'),
            required=False
        )

    def handle(self, *args, **options):
        cup_id = options.get('cup_id')
        if cup_id:
            all_cups_active = Cup.objects.filter(id=cup_id)
        else:
            all_cups_active = Cup.objects.filter(c_active=True)
        for cup in all_cups_active:
            for i in range(1, cup.c_groups + 1):
                print("get games for group:", i)
                all_games = Game.objects.filter(c_id=cup, group_id=i, g_status__in=["yes", "ADJ", "DN"])
                RankGroups.objects.filter(c_id=cup, g_id=i).delete()
                for game in all_games:
                    if game.goals_away is None or game.goals_home is None:
                        continue

                    print(game.t_id_h, game.t_id_v, game.goals_home, game.goals_away)
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
        print("done please clear cache")
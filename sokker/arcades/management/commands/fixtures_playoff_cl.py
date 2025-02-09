# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import Game, Cup, CupTeams, RankGroups
from arcades.utils import generate_fixtures_cl


playoff_fixtures = [
     [9, 9, 24, "e1_cl"],
     [9, 24, 9, "e1_cl"],
     [9, 10 , 23,"e2_cl"],
     [9, 23, 10, "e2_cl"],
     [9, 11, 22, "e3_cl"],
     [9, 22, 11, "e3_cl"],
     [9, 12, 21, "e4_cl"],
     [9, 21, 12, "e4_cl"],
     [9, 13, 20, "e5_cl"],
     [9, 20, 13, "e5_cl"],
     [9, 14, 19, "e6_cl"],
     [9, 19, 14, "e6_cl"],
     [9, 15, 18, "e7_cl"],
     [9, 18, 15, "e7_cl"],
     [9, 16, 17, "e8_cl"],
     [9, 17, 16, "e8_cl"],
     [10, 1, "e8_cl", "e1"],
     [10, "e8_cl", 1, "e1"],
     [10, 2, "e7_cl", "e2"],
     [10, "e7_cl", 2, "e2"],
     [10, 3, "e6_cl", "e3"],
     [10, "e6_cl", 3, "e3"],
     [10, 4, "e5_cl", "e4"],
     [10, "e5_cl", 4, "e4"], 
     [10, 5, "e4_cl", "e5"],
     [10, "e4_cl", 5, "e5"],
     [10, 6, "e3_cl", "e6"],
     [10, "e3_cl", 6, "e6"],
     [10, 7, "e2_cl", "e7"],
     [10, "e2_cl", 7, "e7"],
     [10, 8, "e1_cl", "e8"],
     [10, "e1_cl", 8, "e8"],
     [11, "q1", "q4", "s1"],
     [11, "q4", "q1", "s1"],
     [11, "q2", "q3", "s2"],
     [11, "q3", "e2", "s2"],
     [12, "s1", "s2", "final"]
]


class Command(BaseCommand):
    help = _("Cup fixtures Euro")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--c_id", type=str, help="ID of the cup to perform the draw on."
        )

    def handle(self, *args, **options):
        c_id = options.get("c_id")
        if not c_id:
            self.stdout.write(self.style.ERROR("No c_id provided"))
            return
        # Now you can use the c_id in your logic
        self.stdout.write(self.style.SUCCESS(f"Processing cup with ID: {c_id}"))
        try:
            cup = Cup.objects.get(id=c_id)
            self.stdout.write(self.style.SUCCESS(f"Cup found: {cup.c_name}"))

            # Perform any logic you need with the `cup` object here

        except Cup.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Cup with ID {c_id} does not exist"))
            return

        if cup.c_draw_status == "done" and cup.c_status == "playoff_fixtures" and cup.is_cl:
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)
            ranking_teams = RankGroups.objects.filter(c_id=cup, g_id=1).order_by("-points", "-gdif", "-gscored")
            print(ranking_teams)
            for game in playoff_fixtures:
            
                r = game[0]
                home_team = ranking_teams[int(game[1])]
                away_team = ranking_teams[int(game[2])]
                is_game_played = Game.objects.filter(t_id_h=home_team.t_id, t_id_v=away_team.t_id, c_id=cup, cup_round=r).exists()
                if is_game_played:
                    continue
                
                game = Game()
                game.t_id_h = home_team.t_id
                game.t_id_v = away_team.t_id
                game.c_id = cup
                game.cup_round = int(r)
                game.group_id = 1
                game.playoff_position = game[3]
                game.save()
            cup.c_status = "ready"
            cup.save()

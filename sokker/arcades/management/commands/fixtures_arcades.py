# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import Game, Cup, CupTeams
from arcades.utils import generate_fixtures_cl

fixtures_4 = [[1, 1, 4], [1, 2, 3], [2, 3, 1], [2, 4, 2], [3, 1, 2], [3, 3, 4]]
fixtures_6 = [
    [1, 2, 5],
    [1, 3, 6],
    [1, 4, 1],
    [2, 1, 3],
    [2, 5, 4],
    [2, 6, 2],
    [3, 2, 1],
    [3, 3, 4],
    [3, 6, 5],
    [4, 1, 6],
    [4, 3, 5],
    [4, 4, 2],
    [5, 2, 3],
    [5, 5, 1],
    [5, 6, 4],
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

        if cup.c_draw_status == "done" and cup.c_status == "fixtures":
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)

            group_numbers = list(range(1, cup.c_groups + 1))
            for i in group_numbers:
                ct = CupTeams.objects.filter(c_id=cup, g_id=i).order_by("pot_id")
                print("Group {} team number {}".format(i, ct.count()))
                fixtures = []

                if ct.count() == 4:
                    fixtures = fixtures_4
                if ct.count() == 6:
                    fixtures = fixtures_6
                if ct.count() == 32 and ct.is_cl:
                    fixtures, filename = generate_fixtures_cl()
                for round in fixtures:
                    print(round)
                    r = round[0]
                    home_team = ct[round[1] - 1]
                    away_team = ct[round[2] - 1]
                    print(
                        "Home {} - Away {}".format(
                            home_team.t_id.t_name, away_team.t_id.t_name
                        )
                    )
                    game = Game()
                    game.t_id_h = home_team.t_id
                    game.t_id_v = away_team.t_id
                    game.c_id = cup
                    game.cup_round = r
                    game.group_id = i
                    game.save()
            cup.c_status = "ready"
            cup.save()

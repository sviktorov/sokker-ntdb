# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from sokker_base.models import Team
from sokker_base.api import auth_sokker, get_sokker_team_match_data, get_sokker_match_lineup_data, get_sokker_player_transfer_data
class Command(BaseCommand):
    help = _("Cup fixtures Euro")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--t_id", type=str, help="ID of the team to fetch results"
        )

    def handle(self, *args, **options):
        t_id = options.get("t_id")
        if not t_id:
            self.stdout.write(self.style.ERROR("No t_id provided"))
            return
        # Now you can use the c_id in your logic
        self.stdout.write(self.style.SUCCESS(f"Processing team with ID: {t_id}"))
        try:
            team = Team.objects.filter(country__code=t_id).first()
            self.stdout.write(self.style.SUCCESS(f"Team found: {team.name}"))

            # Perform any logic you need with the `cup` object here

        except Team.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Team with ID {t_id} does not exist"))
            return

        response = auth_sokker()
        season = "71"
        data = get_sokker_team_match_data(t_id, season, response).json()
        for match in data["matches"]:
            match_id = match["id"]
            home_team_id = match["home"]["id"]

            if home_team_id == t_id:
                players= "homePlayers"
            else:
                players= "awayPlayers"
 
            match_data = get_sokker_match_lineup_data(match_id, response).json()

            for player in match_data[players]:
                bench = player["bench"]
                if bench:
                    continue
                print(player)
                exit()
                player_id = player["id"]
                transfer_data = get_sokker_player_transfer_data(player_id, response).json()
                print(transfer_data)
                exit()

                player_name = player["name"]["full"]
                player_number = player["number"]
   
                print(player)
                print(player_id)
                print(player_name)
                print(player_number)
                exit()

               
               
            
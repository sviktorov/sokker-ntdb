# yourapp/management/commands/copy_players_to_archive.py

from django.core.management.base import BaseCommand
from ntdb.models import Player
from sokker_base.api import get_sokker_player_data
from ntdb.pharsers import parser_player
from datetime import datetime


class Command(BaseCommand):
    help = "Update players public skills"

    def handle(self, *args, **options):
        # Query all records from the Player table
        Player.objects.filter(sokker_id__isnull=True).delete()
        players = Player.objects.filter(retired=False).order_by("daily_update")
        today_date = datetime.now().date()
        counter = 0
        for player in players:
            if counter > 500:
                self.stdout.write(
                    self.style.SUCCESS(
                        "1000 Records updated successfully continue later"
                    )
                )
                exit()

            # Send GET request
            if (
                player
                and player.daily_update
                and player.daily_update.date() == today_date
            ):
                print("skip", player.daily_update.date(), player.sokker_id)
                continue
            response = get_sokker_player_data(player.sokker_id)

            if response.status_code == 200:
                player = parser_player(response, player)
                player.save()
                counter = counter + 1
            else:
                print("Error:", response.status_code)
                player.daily_update = today_date
                if response.status_code == 404:
                    player.retired = True
                player.save()

        self.stdout.write(self.style.SUCCESS("Records updated successfully"))

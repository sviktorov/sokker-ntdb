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
        players = Player.objects.all()
        today_date = datetime.now().date()

        for player in players:
            # Send GET request
            if player.daily_update and player.daily_update.date() == today_date:
                print("skip", player.sokker_id)
                continue
            response = get_sokker_player_data(player.sokker_id)
            if response.status_code == 200:
                player = parser_player(response, player)
                player.save()
            else:
                print("Error:", response.status_code)

        self.stdout.write(self.style.SUCCESS("Records copied successfully"))

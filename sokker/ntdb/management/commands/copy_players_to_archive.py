# yourapp/management/commands/copy_players_to_archive.py

from django.core.management.base import BaseCommand
from ntdb.models import Player, ArchivePlayer


class Command(BaseCommand):
    help = "Copies records from Player table to ArchivePlayer table"

    def handle(self, *args, **options):
        # Query all records from the Player table
        players = Player.objects.all()

        # Copy records to ArchivePlayer table
        for player in players:
            # Get archive player by age and country
            print(player.sokker_id, player.name, player.surname, player.age)
            aPlayer = ArchivePlayer.objects.filter(
                sokker_id=player.sokker_id, age=player.age
            ).delete()

            aPlayer = ArchivePlayer()
            # Loop through all attributes of the Player object
            for field in player._meta.fields:
                field_name = field.name
                if field_name == "id" or field_name == "pk":
                    continue
                # Check if the attribute exists in the aPlayer object
                if hasattr(aPlayer, field_name) and hasattr(player, field_name):
                    # Get the attribute value from the Player object
                    field_value = getattr(player, field_name)
                    # Set the attribute value in the ArchivePlayer object
                    setattr(aPlayer, field_name, field_value)
            aPlayer.save()

        self.stdout.write(self.style.SUCCESS("Records copied successfully"))

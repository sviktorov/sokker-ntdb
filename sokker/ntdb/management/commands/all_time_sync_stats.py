# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import ArchivePlayer
from django.db.models import Q, Max
from datetime import datetime
from sokker_base.api import get_sokker_player_data, auth_sokker

class Command(BaseCommand):
    help = "Sync public data archive players"

    def handle(self, *args, **options):
        # Get distinct players with their maximum age
        uniq_sokker_ids = []
        response = auth_sokker()
        players = (
            ArchivePlayer.objects
            .values('sokker_id')
            .annotate(max_age=Max('age'))
            .values('sokker_id', 'max_age')
            .order_by('-max_age')
        )
        print("Players: ", len(players))
        today_date = datetime.now().date()
        msg = _("Player id {} set as {}")
        for player in players:
            if player['sokker_id'] in uniq_sokker_ids:
                continue
            uniq_sokker_ids.append(player['sokker_id'])

            aPlayer = (
                ArchivePlayer.objects
                .filter(
                    sokker_id=player['sokker_id'],
                    age=player['max_age']
                )
                .order_by('-id')
                .first()
            )
            if (
                aPlayer
                and aPlayer.daily_update
                and aPlayer.daily_update.date() == today_date
            ):
                print("skip", aPlayer.daily_update.date(), aPlayer.sokker_id)
                continue

            if aPlayer:
                data = get_sokker_player_data(aPlayer.sokker_id)
                if data.status_code == 200:
                    data = data.json()
                    age = data["info"]["characteristics"]['age']
                    stats = data["info"]["stats"]
                    goals = stats["goals"]
                    assists = stats["assists"]
                    matches = stats["matches"]
                    ntgoals = data["info"]["nationalStats"]["goals"]
                    ntmatches = data["info"]["nationalStats"]["matches"]
                    ntassists = data["info"]["nationalStats"]["assists"]

                    if age == aPlayer.age:
                        # Update stats for existing player
                        aPlayer.goals = goals
                        aPlayer.assists = assists
                        aPlayer.matches = matches
                        aPlayer.ntgoals = ntgoals
                        aPlayer.ntassists = ntassists
                        aPlayer.ntmatches = ntmatches
                        aPlayer.daily_update = today_date
                        aPlayer.save()
                        print(f"Updated stats for player {aPlayer.sokker_id} at age {age}")
                    else:
                        # Create new player record with all fields from aPlayer
                        new_player = ArchivePlayer.objects.create(
                            **{field.name: getattr(aPlayer, field.name) 
                               for field in ArchivePlayer._meta.fields 
                               if field.name != 'id'},  # Copy all fields except id
                        )
                        new_player.daily_update = today_date
                        new_player.age = aPlayer.age +1
                        new_player.goals = goals
                        new_player.assists = assists
                        new_player.matches = matches
                        new_player.ntgoals = ntgoals
                        new_player.ntassists = ntassists
                        new_player.ntmatches = ntmatches
                        new_player.save()
                        print(f"Created new record for player {aPlayer.sokker_id} at age {age}")
                else:
                    print("Error:", data.status_code)
                    aPlayer.daily_update = today_date
                    aPlayer.save()

            
        print(_("Script completed"))

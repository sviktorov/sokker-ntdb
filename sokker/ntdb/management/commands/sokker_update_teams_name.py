# yourapp/management/commands/copy_players_to_archive.py

from django.core.management.base import BaseCommand
from ntdb.models import Player, ArchivePlayer
from sokker_base.models import Team
from sokker_base.api import get_sokker_team_data, auth_sokker
from ntdb.pharsers import parser_team
from datetime import datetime


class Command(BaseCommand):
    help = "Update players public skills"

    def handle(self, *args, **options):
        response = auth_sokker()
        now = datetime.now()
        today_date = datetime.now().date()
        teams = Team.objects.exclude(daily_update__date=today_date).exclude(name__isnull=False).exclude(name='')

        if response:
            # Query all records from the Player table
            teams_done = []

            for team in teams:

                data = get_sokker_team_data(team.pk, response)
                if data.status_code == 200:
                    team = parser_team(data, team)
                    if team:
                        team.daily_update = now
                        print(team.name)
                        team.save()

            print("Teams updated:", len(teams_done))

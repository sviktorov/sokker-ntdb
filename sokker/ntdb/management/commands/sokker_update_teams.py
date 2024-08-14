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
        teams_updated = Team.objects.filter(daily_update__date=today_date).values_list(
            "pk", flat=True
        )

        if response:
            # Query all records from the Player table
            teams_done = []
            distinct_teams = (
                Player.objects.exclude(teamid__in=teams_updated)
                .values("teamid")
                .distinct()
            )

            for teams in distinct_teams:
                teams_done.append(teams["teamid"])
                data = get_sokker_team_data(teams["teamid"], response)
                if data.status_code == 200:
                    team = Team(id=teams["teamid"])
                    team = parser_team(data, team)
                    if team:
                        team.daily_update = now
                        print(team.name)
                        team.save()

            distinct_teams = (
                Player.objects.exclude(youthteamid__in=teams_done)
                .exclude(youthteamid__in=teams_updated)
                .values("youthteamid")
                .distinct()
            )
            for teams in distinct_teams:
                if teams["youthteamid"] not in teams_done:
                    teams_done.append(teams["youthteamid"])
                    data = get_sokker_team_data(teams["youthteamid"], response)
                    if data.status_code == 200:
                        team = Team(id=teams["youthteamid"])
                        team = parser_team(data, team)
                        if team:
                            print(team.name)
                            team.daily_update = now
                            team.save()

            distinct_teams = (
                ArchivePlayer.objects.exclude(teamid__in=teams_done)
                .exclude(teamid__in=teams_updated)
                .values("teamid")
                .distinct()
            )

            for teams in distinct_teams:
                if teams["teamid"] not in teams_done:
                    teams_done.append(teams["teamid"])
                    data = get_sokker_team_data(teams["teamid"], response)
                    if data.status_code == 200:
                        team = Team(id=teams["teamid"])
                        team = parser_team(data, team)
                        if team:
                            print(team.name)
                            team.daily_update = now
                            team.save()

            distinct_teams = (
                ArchivePlayer.objects.exclude(youthteamid__in=teams_done)
                .values("youthteamid")
                .distinct()
            )
            for teams in distinct_teams:
                if teams["youthteamid"] not in teams_done:
                    teams_done.append(teams["youthteamid"])
                    data = get_sokker_team_data(teams["youthteamid"], response)
                    if data.status_code == 200:
                        team = Team(id=teams["youthteamid"])
                        team = parser_team(data, team)
                        if team:
                            print(team.name)
                            team.daily_update = now
                            team.save()
            print("Teams updated:", len(teams_done))
        self.stdout.write(self.style.SUCCESS("Records copied successfully"))

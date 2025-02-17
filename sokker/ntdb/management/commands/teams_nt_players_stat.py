# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import ArchivePlayer, NTTeamsStats
import json
class Command(BaseCommand):
    help = "Calculate nt team stats ntplayers count"

    def add_arguments(self, parser):
        parser.add_argument(
            '--country_code',
            type=str,
            help=_('Filter players by country code (e.g., 54)'),
            required=True,
        )

    def handle(self, *args, **options):
        country_code = options['country_code']
        # Initialize dictionary to store team stats
        team_stats = {}  # {teamid: total_games}
        youth_team_stats = {} # {teamid: total_games}
        players_in_team = {}  # {teamid: total_players}
        youth_players_in_team = {}
        players = ArchivePlayer.objects.filter(countryid=country_code).filter(ntmatches__gt=0)
        unique_players = []
        unique_players_youth = []
        count = 0
        for player in players:  
            if player.sokker_id in unique_players_youth:
                continue
            count += 1
            unique_players_youth.append(player.sokker_id)
            age_seasons = ArchivePlayer.objects.filter(sokker_id=player.sokker_id).order_by("-age", "-ntmatches")
            previous_age = 0
            player_youth_teams_ids = []
            for age_season in age_seasons:
                if not age_season.youthteamid or age_season.youthteamid == "NA":
                    continue
                current_age = age_season.age
                if previous_age == current_age:
                    continue
                previous_age = current_age
           
                if age_season.youthteamid in  player_youth_teams_ids:
                    continue
                player_youth_teams_ids.append(age_season.youthteamid)
                if age_season.youthteamid in youth_team_stats:
                    youth_team_stats[age_season.youthteamid] = youth_team_stats[age_season.youthteamid] + 1
                    youth_players_in_team[age_season.youthteamid].append(player.sokker_id)
                else:
                    youth_team_stats[age_season.youthteamid] = 1
                    youth_players_in_team[age_season.youthteamid] = [player.sokker_id]        
        
        print("Youth Team Statistics:")
        for teamid, total_games in youth_team_stats.items():
            stat = NTTeamsStats.objects.filter(countryid=country_code, stat_type="youth", teamid=teamid).first()
            if stat:
                stat.ntplayers = total_games
                stat.json_data_youth = json.dumps(youth_players_in_team[teamid])
                stat.save()
            else:
                stat = NTTeamsStats()
                stat.countryid = country_code
                stat.stat_type = "youth"
                stat.teamid = teamid
                stat.ntplayers = total_games
                stat.json_data_youth = json.dumps(youth_players_in_team[teamid])
                stat.save()
            print(f"Team {teamid}: {total_games} youth players")

        count = 0
        for player in players:  
            if player.sokker_id in unique_players:
                continue
            count += 1
            unique_players.append(player.sokker_id)
            print(player.sokker_id, player.name, player.surname)
            age_seasons = ArchivePlayer.objects.filter(sokker_id=player.sokker_id).order_by("-age", "-ntmatches")
            previous_age = 0
            player_teams_ids = []
            for age_season in age_seasons:
                if not age_season.teamid or age_season.teamid == "NA":
                    continue
                current_age = age_season.age
                if previous_age == current_age:
                    continue
                previous_age = current_age
           
                if age_season.teamid in player_teams_ids:
                    continue
                player_teams_ids.append(age_season.teamid)
                if age_season.teamid in team_stats:
                    team_stats[age_season.teamid] = team_stats[age_season.teamid] + 1
                    players_in_team[age_season.teamid].append(player.sokker_id)
                else:
                    team_stats[age_season.teamid] = 1
                    players_in_team[age_season.teamid] = [player.sokker_id]
        # Print final team statistics
        print("Team Statistics:")
        for teamid, total_games in team_stats.items():
            print(teamid, total_games)
            stat = NTTeamsStats.objects.filter(countryid=country_code, stat_type="team", teamid=teamid).first()
            if stat:
                stat.ntplayers = total_games
                stat.json_data = json.dumps(players_in_team[teamid])
                stat.save()
            else:
                stat = NTTeamsStats()
                stat.countryid = country_code
                stat.stat_type = "team"
                stat.teamid = teamid
                stat.ntplayers = total_games
                stat.json_data = json.dumps(players_in_team[teamid])
                stat.save()
            print(f"Team {teamid}: {total_games} players")

        print(_("Script completed"))

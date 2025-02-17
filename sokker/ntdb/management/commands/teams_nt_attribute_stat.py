# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import ArchivePlayer, NTTeamsStats
from ntdb.utils import get_player_stat_for_age_season_type
class Command(BaseCommand):
    help = "Calculate nt team stats assists"

    def add_arguments(self, parser):
        parser.add_argument(
            '--stat-type',
            type=str,
            choices=['youth', 'team'],
            default='both',
            help='Type of statistics to calculate: youth, team, or both'
        )
        parser.add_argument(
            '--stat-field',
            type=str,
            choices=['ntassists', 'ntgoals', 'ntmatches'],
            default='None',
            help='Type of statistics to calculate: youth, team, or both'
        )
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
        stat_type = options['stat_type']
        if stat_type not in ['youth', 'team']:
            print("Please specify stat type")
            return
        stat_field = options['stat_field']
        if stat_field not in ['ntassists', 'ntgoals', 'ntmatches']:
            print("Please specify stat field")
            return
        max_limit = 0
        if stat_field == "ntmatches":
            max_limit = 16
            players = ArchivePlayer.objects.filter(countryid=country_code).filter(ntmatches__gt=0)
            sort_field = "-ntmatches"
        elif stat_field == "ntgoals":
            players = ArchivePlayer.objects.filter(countryid=country_code).filter(ntgoals__gt=0)
            sort_field = "-ntgoals"
        elif stat_field == "ntassists":
            players = ArchivePlayer.objects.filter(countryid=country_code).filter(ntassists__gt=0)
            sort_field = "-ntassists"
        unique_players = []
        count = 0

        for player in players:  
            if player.sokker_id in unique_players:
                continue
            count += 1
            unique_players.append(player.sokker_id)
            age_seasons = ArchivePlayer.objects.filter(sokker_id=player.sokker_id).order_by("-age", sort_field)
            previous_age = 0
            for age_season in age_seasons:
                if stat_type == "team":
                    if not age_season.teamid or age_season.teamid == "NA":
                        continue
                elif stat_type == "youth":
                    if not age_season.youthteamid or age_season.youthteamid == "NA":
                        continue
                current_age = age_season.age
                if previous_age == current_age:
                    continue
                previous_age = current_age
                games = get_player_stat_for_age_season_type(player.sokker_id, age_season.age, stat_field, max_limit) 
                # print(age_season.age, games, age_season.teamid, age_season.ntassists)              
                if games > 0:
                    if stat_type == "team":
                        if age_season.teamid in team_stats:
                            team_stats[age_season.teamid] = team_stats[age_season.teamid] + games
                        else:
                            team_stats[age_season.teamid] = games
                    elif stat_type == "youth":
                        if age_season.youthteamid in team_stats:
                            team_stats[age_season.youthteamid] = team_stats[age_season.youthteamid] + games
                        else:
                            team_stats[age_season.youthteamid] = games
        
        # Print final team statistics
        print(f"{stat_type} Statistics:")
        for teamid, total_games in team_stats.items():
            # print(teamid, total_games)
            stat = NTTeamsStats.objects.filter(countryid=country_code, stat_type=stat_type, teamid=teamid).first()
            if stat:
                setattr(stat, stat_field, total_games)
                stat.save()
            else:
                stat = NTTeamsStats()
                stat.countryid = country_code
                stat.stat_type = stat_type
                stat.teamid = teamid
                setattr(stat, stat_field, total_games)
                stat.save()
            print(f"Team {teamid}: {total_games} {stat_field}")

        print(_("Script completed"))

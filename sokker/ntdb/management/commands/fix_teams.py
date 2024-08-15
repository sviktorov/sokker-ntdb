# yourapp/management/commands/copy_players_to_archive.py

from django.core.management.base import BaseCommand
from sokker_base.models import Team
from sokker_base.api import get_sokker_team_data, auth_sokker, get_sokker_team_data
from ntdb.pharsers import parser_team
from django.db import connection


def get_archived_players_missing_team_ids():
    with connection.cursor() as cursor:
        query = """
            SELECT distinct(teamid) 
            FROM ntdb_archiveplayer 
            WHERE teamid NOT IN (
                SELECT id 
                FROM sokker_base_team
            )
        """
        cursor.execute(query)
        result = cursor.fetchall()

    return [row[0] for row in result]


def get_archived_players_missing_youth_team_ids():
    with connection.cursor() as cursor:
        query = """
            SELECT distinct(youthteamid) 
            FROM ntdb_archiveplayer 
            WHERE youthteamid NOT IN (
                SELECT id 
                FROM sokker_base_team
            )
        """
        cursor.execute(query)
        result = cursor.fetchall()

    return [row[0] for row in result]


def get_players_missing_team_ids():
    with connection.cursor() as cursor:
        query = """
            SELECT distinct(teamid) 
            FROM ntdb_player 
            WHERE teamid NOT IN (
                SELECT id 
                FROM sokker_base_team
            )
        """
        cursor.execute(query)
        result = cursor.fetchall()

    return [row[0] for row in result]


def get_players_missing_youth_team_ids():
    with connection.cursor() as cursor:
        query = """
            SELECT distinct(youthteamid) 
            FROM ntdb_player 
            WHERE youthteamid NOT IN (
                SELECT id 
                FROM sokker_base_team
            )
        """
        cursor.execute(query)
        result = cursor.fetchall()

    return [row[0] for row in result]


def fix_teams(teams, response):
    for team_id in teams:
        print(team_id)
        data = get_sokker_team_data(team_id, response)
        if data.status_code == 200:
            team = Team(id=team_id)
            team = parser_team(data, team)
            if team:
                print(team.name)
                team.save()
            else:
                team = Team(id=team_id)
                team.name = "NA"
                team.country = None
                team.save()


def set_player_teamid_to_null():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE ntdb_player 
            SET teamid = NULL 
            WHERE teamid = 0;
        """
        )


def set_player_youth_teamid_to_null():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE ntdb_player 
            SET youthteamid = NULL 
            WHERE youthteamid = 0;
        """
        )


def set_archive_player_teamid_to_null():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE ntdb_archiveplayer 
            SET teamid = NULL 
            WHERE teamid = 0;
        """
        )


def set_archive_player_youth_teamid_to_null():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE ntdb_archiveplayer 
            SET youthteamid = NULL 
            WHERE youthteamid = 0;
        """
        )


class Command(BaseCommand):
    help = "Update players public skills"

    def handle(self, *args, **options):
        # set_player_teamid_to_null()
        # set_player_youth_teamid_to_null()
        # set_archive_player_teamid_to_null()
        # set_archive_player_youth_teamid_to_null()

        response = auth_sokker()
        get_sokker_team_data(10230, response)

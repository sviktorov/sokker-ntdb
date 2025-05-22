from sokker_base.api import extract_table_from_html, get_sokker_league_table_data, auth_sokker, get_sokker_archive_table_data
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from sokker_base.models import LeagueTable, Country, Team   
from django.core.management import call_command

class Command(BaseCommand):
    help = _("Fetch league tables")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--league_id", type=str, help="ID of the league to fetch league table for."
        )
        parser.add_argument(
            "--country_id", type=str, help="ID of the country to fetch league table for."
        )
        parser.add_argument(
            "--season_id", type=str, help="ID of the season to fetch league table for."
        )   

    def handle(self, *args, **options):
        league_id = options.get("league_id")
        country_id = options.get("country_id")
        season_id = options.get("season_id")
        if not league_id:
            self.stdout.write(self.style.ERROR("No league_id provided"))
            return
        if not country_id:
            self.stdout.write(self.style.ERROR("No country_id provided"))
            return
        if not season_id:
            self.stdout.write(self.style.ERROR("No season_id provided"))
            return

        cookie = auth_sokker()
        season_id = int(season_id)
        if season_id > 52:
            round_id = 22
        else:
            round_id = 14

        league_table_data = get_sokker_archive_table_data(league_id, season_id, round_id, cookie)
        table = extract_table_from_html(league_table_data.text, 1)
        headers, rows = table_to_headers_and_rows(table)    
        country = Country.objects.filter(code=country_id).first()
        if not country:
            self.stdout.write(self.style.ERROR("No country found"))
            return
        for row in rows:
            team = Team.objects.filter(id=row[1]).first()
            if not team:
                team = Team.objects.create(id=row[1], name=row[2])
                self.stdout.write(self.style.SUCCESS(f"Team {row[1]} created"))
            league_table = LeagueTable.objects.filter(league=league_id, country=country, team=team, season=season_id).first()
            if not league_table:
                LeagueTable.objects.create(
                    league=league_id,
                    country=country,
                    team=team,
                    season=season_id,
                    position=row[0],
                    played=row[3],
                    won=row[4],
                    drawn=row[5],
                    lost=row[6],    
                    scored=row[7],
                    conceded=row[8],
                    points=row[9]
                )
            else:
                league_table.position=row[0]
                league_table.played=row[3]
                league_table.won=row[4]
                league_table.drawn=row[5]
                league_table.lost=row[6]   
                league_table.scored=row[7]
                league_table.conceded=row[8]
                league_table.points=row[9]
                league_table.save()
            self.stdout.write(self.style.SUCCESS(f"League table {league_id} {country_id} {team.name} {season_id} {row[0]} created"))


def table_to_headers_and_rows(table):
    """
    Converts a BeautifulSoup table element to headers and rows.
    Returns (headers, rows) where headers is a list and rows is a list of lists.
    """
    # Extract headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        counter = 0
        for th in header_row.find_all(['th', 'td']):
            counter += 1
            if counter == 1:
                headers.append("Position")
            elif counter == 2:
                headers.append("Team ID")
                headers.append("Team Name")
            elif counter == 7:
                headers.append("Scored")
                headers.append("Conceded")
            else:
                headers.append(th.get_text(strip=False))
    
    # Extract rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip header row
        row = []
        counter = 0
        for td in tr.find_all(['td', 'th']):
            counter += 1
            if counter == 1:
                row.append(td.get_text(strip=True).replace(".", ""))
            elif counter == 2:
                link = td.find('a')
                if link:
                    team_id = link.get('href').split('/')[-1]
                    row.append(team_id)
                else:
                    row.append(None)
                row.append(td.get_text(strip=False))
            elif counter == 7:
                gs = td.get_text(strip=True)
                scored = gs.split('-')[0]
                conceded = gs.split('-')[1]
                row.append(scored)
                row.append(conceded)
            else:
                row.append(td.get_text(strip=False))
        rows.append(row)
    
    return headers, rows


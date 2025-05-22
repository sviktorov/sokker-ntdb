from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import EuroCupGameStats, Game, Cup, Player
from sokker_base.models import Country
from sokker_base.api import extract_table_from_html, get_sokker_match_data,get_sokker_match_stats_data,get_sokker_game_lineup_stats_html, auth_sokker, get_sokker_match_lineup_data, get_sokker_player_data
import re


def table_to_headers_and_rows(table):
    """
    Converts a BeautifulSoup table element to headers and rows.
    Returns (headers, rows) where headers is a list and rows is a list of lists.
    """
    # Extract headers
    headers = []
    if not table:
        return headers, []
    header_row = table.find('tr')
    if header_row:
        counter = 0
        for th in header_row.find_all(['th', 'td']):
            counter += 1
            if counter == 2:
                headers.append("Player ID")
                headers.append("Goals")
                headers.append("Assists")
                headers.append("Red Cards")
                headers.append("Yellow Cards")
            headers.append(th.get_text(strip=True))
    
    # Extract rows
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip header row
        row = []
        counter = 0
        for td in tr.find_all(['td', 'th']):
            counter += 1
        
            if counter == 2:
                link = td.find('a')
                goals = 0
                assits = 0
                red_cards = 0
                yellow_cards = 0
                pid = None
                if link:
                    href = link.get('href') 
                    pid = href.split('/')[-1]      
                    images  = td.find_all('img')
                    for image in images:
                        if image.get('src').find('gool.gif') != -1:
                            goals += 1
                        elif image.get('src').find('assist.gif') != -1:
                            assits += 1
                        elif image.get('src').find('czerwona.gif') != -1:
                            red_cards += 1
                        elif image.get('src').find('zolta.gif') != -1:
                            yellow_cards += 1
                row.append(pid)
                row.append(goals)
                row.append(assits)
                row.append(red_cards)
                row.append(yellow_cards)
            else:
                row.append(td.get_text(strip=True))
        rows.append(row)
    
    return headers, rows

def add_spaces_to_uppercase(paname):
    # If there's only one word or no uppercase letters, return as is
    if not any(c.isupper() for c in paname[1:]):
        return paname
    
    # Add space before uppercase letters (except first character)
    result = paname[0]  # Keep first character as is
    for char in paname[1:]:
        if char.isupper():
            result += ' ' + char
        else:
            result += char
    return result

def update_game_stats(rows, game, team):
    for row in rows:
        pid = row[1]
        if not pid:
            continue

        goals = row[2]
        assits = row[3]
        red_cards = row[4]
        yellow_cards = row[5]
        if goals > 0 or assits > 0 or red_cards > 0 or yellow_cards > 0:
            player = Player.objects.filter(id=pid).first()
            if not player:
                country = Country.objects.filter(code=team.t_sokker_id).first()
                player = Player(id=pid, country_id=country)
                name = get_sokker_player_data(pid).json()["info"]["name"]["full"]
                player.name = name
                player.save()
            print(pid, goals, assits, red_cards, yellow_cards)
            cup_stats = EuroCupGameStats.objects.filter(player_id=pid, game_id=game, team_id=team).first()
            if not cup_stats:
                cup_stats = EuroCupGameStats(player_id=player, game_id=game, team_id=team)
            cup_stats.goals = goals
            cup_stats.assists = assits
            cup_stats.red_cards = red_cards
            cup_stats.yellow_cards = yellow_cards
            cup_stats.save()
    return True

class Command(BaseCommand):
    help = _("Cup fixtures Euro")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--c_id", type=str, help="ID of the cup to perform the draw on."
        )

    def handle(self, *args, **options):
        c_id = options.get("c_id")
        if not c_id:
            self.stdout.write(self.style.ERROR("No c_id provided"))
            return
        self.stdout.write(self.style.SUCCESS(f"Fetching game details for cup {c_id}"))

        cup = Cup.objects.get(id=c_id)
        games = Game.objects.filter(c_id=cup, g_status__in=["yes", "ADJ"], has_stats=False)
        cookie = auth_sokker()
        for game in games:
            self.stdout.write(self.style.SUCCESS(f"Game {game.id} - {game.t_id_h} vs {game.t_id_v}"))
            if game.matchID:
                ## details = get_sokker_match_data(game.matchID, cookie).json()
                ## home stats
                home_stats = get_sokker_game_lineup_stats_html(game.matchID, game.t_id_h.t_sokker_id, cookie)
                home_stats_table = extract_table_from_html(home_stats.text, 0)
                headers, rows = table_to_headers_and_rows(home_stats_table)
                update_game_stats(rows, game, game.t_id_h)
                away_stats = get_sokker_game_lineup_stats_html(game.matchID, game.t_id_v.t_sokker_id, cookie)
                away_stats_table = extract_table_from_html(away_stats.text, 0)
                headers, rows = table_to_headers_and_rows(away_stats_table)
                update_game_stats(rows, game, game.t_id_v)
                game.has_stats = True
                game.save()
  




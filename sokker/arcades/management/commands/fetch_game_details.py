from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import CupGameStats, Game, Cup, CupTeams, GameDetails, Player
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
                player = Player(id=pid, team_id=team, country_id=team.country)
                name = get_sokker_player_data(pid).json()["info"]["name"]["full"]
                player.name = name
                player.save()
            print(pid, goals, assits, red_cards, yellow_cards)
            cup_stats = CupGameStats.objects.filter(player_id=pid, game_id=game).first()
            if not cup_stats:
                cup_stats = CupGameStats(player_id=player, game_id=game)
            cup_stats.goals = goals
            cup_stats.assists = assits
            cup_stats.red_cards = red_cards
            cup_stats.yellow_cards = yellow_cards
            cup_stats.team_id = team
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
            if game.matchID and int(game.matchID)>0:
                details = get_sokker_match_stats_data(game.matchID, cookie).json()
                game_details_home = GameDetails.objects.filter(game_id=game, team_id=game.t_id_h, is_home=True).first()
                game_details_away = GameDetails.objects.filter(game_id=game, team_id=game.t_id_v, is_home=False).first()
                if not game_details_home:
                    game_details_home = GameDetails(game_id=game, team_id=game.t_id_h, is_home=True)
                if not game_details_away:
                    game_details_away = GameDetails(game_id=game, team_id=game.t_id_v, is_home=False)
                
                game_details_home.timeOnHalf = details["home"]["timeOnHalf"]
                game_details_home.timePossession = details["home"]["timePossession"]
                game_details_home.shots = details["home"]["shoots"]
                game_details_home.fouls = details["home"]["fouls"]
                game_details_home.yellowCards = details["home"]["yellowCards"]
                game_details_home.redCards = details["home"]["redCards"]
                game_details_home.offsides = details["home"]["offsides"]
                game_details_home.effShoot = details["home"]["effShoot"]
                game_details_home.effPass = details["home"]["effPass"]
                game_details_home.effTackle = details["home"]["effTackle"]
                game_details_home.save()
                game_details_away.timeOnHalf = details["away"]["timeOnHalf"]
                game_details_away.timePossession = details["away"]["timePossession"]
                game_details_away.shots = details["away"]["shoots"]
                game_details_away.fouls = details["away"]["fouls"]
                game_details_away.yellowCards = details["away"]["yellowCards"]
                game_details_away.redCards = details["away"]["redCards"]
                game_details_away.offsides = details["away"]["offsides"]
                game_details_away.effShoot = details["away"]["effShoot"]
                game_details_away.effPass = details["away"]["effPass"]
                game_details_away.effTackle = details["away"]["effTackle"]
                game_details_away.save()
                ## home stats
                home_stats = get_sokker_game_lineup_stats_html(game.matchID, game.t_id_h.id, cookie)
                home_stats_table = extract_table_from_html(home_stats.text, 0)
                headers, rows = table_to_headers_and_rows(home_stats_table)
                update_game_stats(rows, game, game.t_id_h)
                away_stats = get_sokker_game_lineup_stats_html(game.matchID, game.t_id_v.id, cookie)
                away_stats_table = extract_table_from_html(away_stats.text, 0)
                headers, rows = table_to_headers_and_rows(away_stats_table)
                update_game_stats(rows, game, game.t_id_v)
                game.has_stats = True
                game.save()
  




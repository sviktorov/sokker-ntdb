from itertools import combinations, permutations

import random
import os
import sys
import json
from functools import lru_cache
from datetime import datetime, timedelta
from PIL import Image, UnidentifiedImageError
import os
from django.conf import settings
import requests
from io import BytesIO
import cairosvg
from django.core.cache import cache
import hashlib
from PIL import ImageDraw, ImageFont
import matplotlib.font_manager as fm
from django.http import HttpResponse
import io
import matplotlib.font_manager as fm
# Increase the recursion depth to a higher value (e.g., 5000)
sys.setrecursionlimit(130000)

DRAW_STATUS_CHOICES = [
    ('ready', 'Ready'),
    ('done', 'Done'),
    ('signup', 'Signup'),
]

CUP_STATUS_CHOICES = [
    ('ready', 'Ready'),
    ('done', 'Done'),
    ('signup', 'Signup'),
    ('draw', 'Draw'),   
    ('fixtures', 'Fixtures'),
]


CL_TEAMS = [
        list(range(1, 10)),    # Pot 1: Teams 1 to 9
        list(range(10, 19)),   # Pot 2: Teams 10 to 18
        list(range(19, 28)),   # Pot 3: Teams 19 to 27
        list(range(28, 37)),   # Pot 4: Teams 28 to 36
    ]


PLAYOFF_FIXTURES_CL = [
    [9, 16, 17, "e1_cl", 1],
    [9, 9, 24, "e2_cl", 8],
    [9, 12, 21, "e3_cl", 5],
    [9, 13, 20, "e4_cl", 4], 
    [9, 15, 18, "e5_cl", 2], 
    [9, 10 , 23,"e6_cl", 7],
    [9, 11, 22, "e7_cl", 6],
    [9, 14, 19, "e8_cl", 3],
    [10, "e1_cl", 1, "e1"],
    [10, "e2_cl", 8, "e2"],
    [10, "e3_cl", 5, "e3"],
    [10, "e4_cl", 4, "e4"],
    [10, "e5_cl", 2, "e5"],
    [10, "e6_cl", 7, "e6"],
    [10, "e7_cl", 6, "e7"],
    [10, "e8_cl", 3, "e8"],
    [11, "e1", "e2", "q1"],
    [11, "e3", "e4", "q2"],
    [11, "e5", "e6", "q3"],
    [11, "e7", "e8", "q4"],
    [12, "q1", "q2", "s1"],
    [12, "q3", "q4", "s2"],
    [13, "s1", "s2", "final"]
]


def get_next_day(date_str):
    """
    Get the next day from a given date string.
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD'
        
    Returns:
        str: Next day's date in format 'YYYY-MM-DD'
    """
    current_date = datetime.strptime(date_str, '%Y-%m-%d')
    next_date = current_date + timedelta(days=1)
    return next_date.strftime('%Y-%m-%d')

def get_previous_day(date_str):
    """
    Get the next day from a given date string.
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD'
        
    Returns:
        str: Next day's date in format 'YYYY-MM-DD'
    """
    current_date = datetime.strptime(date_str, '%Y-%m-%d')
    next_date = current_date - timedelta(days=1)
    return next_date.strftime('%Y-%m-%d')

def get_next_monday_or_thursday(start_date):
    """
    Get the next Monday or Thursday from the given date.

    Args:
        start_date (str or datetime): The date to start from. Can be a string in format 'YYYY-MM-DD' 
                                    or a datetime object.

    Returns:
        datetime: The next Monday or Thursday.
    """
    # Handle empty or None input by using current date
    if not start_date:
        start_date = datetime.now()
    
    # Convert string to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            # Handle invalid date string by using current date
            start_date = datetime.now()

    days_ahead_monday = (7 - start_date.weekday() + 0) % 7  # 0 for Monday
    days_ahead_thursday = (7 - start_date.weekday() + 3) % 7  # 3 for Thursday

    if days_ahead_monday == 0:  # If today is Monday
        days_ahead_monday = 7
    if days_ahead_thursday == 0:  # If today is Thursday
        days_ahead_thursday = 7

    next_monday = start_date + timedelta(days=days_ahead_monday)
    next_thursday = start_date + timedelta(days=days_ahead_thursday)

    return min(next_monday, next_thursday)

def get_next_monday_or_saturday(start_date):
    """
    Get the next Monday or Saturday from the given date.

    Args:
        start_date (str or datetime): The date to start from. Can be a string in format 'YYYY-MM-DD' 
                                    or a datetime object.

    Returns:
        datetime: The next Monday or Saturday.
    """
    # Handle empty or None input by using current date
    if not start_date:
        start_date = datetime.now()
    
    # Convert string to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            # Handle invalid date string by using current date
            start_date = datetime.now()

    days_ahead_monday = (7 - start_date.weekday() + 0) % 7  # 0 for Monday
    days_ahead_saturday = (7 - start_date.weekday() + 5) % 7  # 5 for Saturday

    if days_ahead_monday == 0:  # If today is Monday
        days_ahead_monday = 7
    if days_ahead_saturday == 0:  # If today is Saturday
        days_ahead_saturday = 7

    next_monday = start_date + timedelta(days=days_ahead_monday)
    next_saturday = start_date + timedelta(days=days_ahead_saturday)

    return min(next_monday, next_saturday)

def get_next_saturday(start_date):
    """
    Get the next Saturday from the given date.

    Args:
        start_date (str or datetime): The date to start from. Can be a string in format 'YYYY-MM-DD' 
                                    or a datetime object.

    Returns:
        datetime: The next Saturday.
    """
    # Handle empty or None input by using current date
    if not start_date:
        start_date = datetime.now()
    
    # Convert string to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            # Handle invalid date string by using current date
            start_date = datetime.now()

    days_ahead = (7 - start_date.weekday() + 5) % 7  # 5 for Saturday

    if days_ahead == 0:  # If today is Saturday
        days_ahead = 7

    next_saturday = start_date + timedelta(days=days_ahead)
    return next_saturday


def get_next_thursday(start_date):
    """
    Get the next Thursday from the given date.

    Args:
        start_date (str or datetime): The date to start from. Can be a string in format 'YYYY-MM-DD' 
                                    or a datetime object.

    Returns:
        datetime: The next Thursday.
    """
    # Handle empty or None input by using current date
    if not start_date:
        start_date = datetime.now()
    
    # Convert string to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            # Handle invalid date string by using current date
            start_date = datetime.now()

    days_ahead = (7 - start_date.weekday() + 3) % 7  # 3 for Thursday

    if days_ahead == 0:  # If today is Thursday
        days_ahead = 7

    next_thursday = start_date + timedelta(days=days_ahead)
    return next_thursday

# Function to save fixtures to a file
def save_fixtures_to_file(fixtures, filename="fixtures.json"):
    with open(filename, "w") as file:
        json.dump(fixtures, file)
    print(f"Fixtures saved to {filename}")

# Function to load fixtures from a file if it exists
def load_fixtures_from_file(filename="fixtures.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            fixtures = json.load(file)
        print(f"Fixtures loaded from {filename}")
        return fixtures
    return None

def generate_team_pairs(team, other_teams, is_home):
    """
    Generate all pairs where the specified team is either the first or second element.
    
    Args:
        team (str): The specific team to include in pairs.
        other_teams (list): A list of other teams to pair with.
        
    Returns:
        list: A list of tuples representing the pairs.
    """
    # Create pairs where team is the first or second element
    if is_home:
        pairs = [(team, other_team) for other_team in other_teams] 
    else:
        pairs = [(other_team, team) for other_team in other_teams]
    return pairs

@lru_cache(maxsize=None)
def pot_for_team(team):
    pots = CL_TEAMS
    counter=0
    for pot in pots:
        if team in pot:
            return counter
        counter=counter+1
    return False

def pairs_team_pot(pot, team, is_home):
    pots = CL_TEAMS
    return generate_team_pairs(team, pots[pot], is_home)

def generate_round_robin_fixtures(number_teams):
    teams = list(range(1, number_teams + 1))  # Convert range to list
    rounds = []
    all_previous_matches = set()  # To store already played pairs

    for round_num in range(number_teams-1):  # Assuming 7 rounds for 8 teams
        round_fixtures = []
        random.shuffle(teams)  # Shuffle teams to randomize matchups
        
        # Create matchups for this round by pairing up the teams
        for i in range(0, len(teams), 2):
            match = tuple(sorted([teams[i], teams[i+1]]))  # Sort to avoid reversing pairs
            
            # Ensure that the match has not already occurred in previous rounds
            while match in all_previous_matches:
                random.shuffle(teams)  # Reshuffle if there is a repetition
                match = tuple(sorted([teams[i], teams[i+1]]))
            
            round_fixtures.append([teams[i], teams[i+1]])
            all_previous_matches.add(match)  # Add the current match to the set
        
        rounds.append(round_fixtures)

    return rounds




def generate_fixtures_cl_32():
    """
    Generate fixtures for 32 teams in 8 groups of 4 teams.
    The first 7 rounds will be inter-group, and the last round (round 8) will be intra-group games.
    
    Returns:
        list: A list of 8 rounds, each round containing 16 games in the format [round, home_id, away_id].
    """
    # Step 1: Split 32 teams into 4 pots, each with 8 teams
    pots_fixtures = generate_round_robin_fixtures(8)

    pots = [
        list(range(1, 5)),    # Pot 1: Teams 1 to 4
        list(range(5, 9)),    # Pot 2: Teams 5 to 8
        list(range(9, 13)),   # Pot 3: Teams 9 to 12
        list(range(13, 17)),   # Pot 4: Teams 13 to 16
        list(range(17, 21)),  # Pot 5: Teams 17 to 20
        list(range(21, 25)),  # Pot 6: Teams 21 to 24
        list(range(25, 29)),   # Pot 7: Teams 25 to 28
        list(range(29, 33))   # Pot 8: Teams 29 to 32
    ]
    rounds = []
    round_number = 0
    for round  in pots_fixtures:
        round_number=round_number+1
        games = []
        for pair in round:
            pot_home = pots[pair[0]-1]
            pot_away = pots[pair[1]-1]
            paired = list(zip(pot_home, pot_away))
            # Print the pairs
            for pair in paired:
                games.append([round_number, pair[0], pair[1]])
        rounds.append(games)


    round_number = 8
    games = []
    for pot in pots:
        random.shuffle(pot)
        games.append([round_number, pot[0], pot[1]])
        games.append([round_number, pot[2], pot[3]])
    rounds.append(games)
    return rounds

def generate_unique_fixtures(teams, num_rounds, num_pairs_per_round):

    matrix_teams = []
    for pot in CL_TEAMS:
        for team in pot:
            matrix_teams.append(
                {
                    team: {
                        "home": 0,
                        "away": 0,
                        "pot1": 0,
                        "pot2": 0,
                        "pot3": 0,
                        "pot4": 0,
                    }
                }
            )   
    # Generate all possible pairs
    all_possible_pairs = list(permutations(teams, 2))
    print(len(all_possible_pairs))
    random.shuffle(all_possible_pairs)  # Shuffle to introduce randomness
    # Keep track of used pairs
    used_pairs = set()
    rounds = []

    for round_num in range(num_rounds):
        round_pairs = []
        available_pairs = [pair for pair in all_possible_pairs if pair not in used_pairs]

        # Generate pairs for the current round
        while len(round_pairs) < num_pairs_per_round and available_pairs:
            pair = available_pairs.pop(0)  # Pick the first pair
            # Check if teams in the pair are already used in the current round
            if any(pair[0] in p or pair[1] in p for p in round_pairs):
                continue
        
        round_pairs = []
        pairs_pool = [pair for pair in all_possible_pairs if pair not in used_pairs]
        # Sort pairs based on a heuristic (e.g., least used teams)
        if round_num == 0:
            random.shuffle(pairs_pool)  # Shuffle to pick pairs randomly
        else:
            pairs_pool.sort(key=lambda pair: (
                matrix_teams[pair[0] - 1][pair[0]]["home"] + 
                matrix_teams[pair[1] - 1][pair[1]]["away"]
            ))
        
        # Pick unique pairs for this round
        for pair in pairs_pool:
            if len(round_pairs) >= num_pairs_per_round:
                break
            # Ensure no team is reused in this round
            if any(pair[0] in p or pair[1] in p for p in round_pairs):
                continue

            matrix_teams[pair[0] - 1][pair[0]]["home"] = matrix_teams[pair[0] - 1][pair[0]]["home"] +1
            matrix_teams[pair[1] - 1][pair[1]]["away"] = matrix_teams[pair[1] - 1][pair[1]]["away"] +1

            oposit_pair = (pair[1], pair[0])
            round_pairs.append(pair)
            used_pairs.add(pair)
            used_pairs.add(oposit_pair)
            pot_home = pot_for_team(pair[0])
            pot_away = pot_for_team(pair[1])
            home_pairs = pairs_team_pot(pot_home, pair[1], False)
            away_pairs = pairs_team_pot(pot_away, pair[0], True)

            for p in home_pairs:
                used_pairs.add(p)
            for p in away_pairs:
                used_pairs.add(p)

        
        # Check if we successfully generated the required pairs
        if len(round_pairs) < num_pairs_per_round:
            break
        
        round_games = []
        for pair in round_pairs:
            round_games.append([round_num+1, pair[0], pair[1]])
        rounds.append(round_games)
    
    if len(rounds) < num_rounds:
        print("Retrying fixture generation due to insufficient rounds.")
        return generate_unique_fixtures(teams, num_rounds, num_pairs_per_round)

    
    return rounds


def generate_fixtures_cl():
    """
    Generate fixtures for 36 teams in 9 teams of 4 teams.
    The first 7 rounds will be inter-group, and the last round (round 8) will be intra-group games.
    
    Returns:
        list: A list of 8 rounds, each round containing 16 games in the format [round, home_id, away_id].
    """

    filename = "cl.json"
    fixtures = load_fixtures_from_file(filename)
    if fixtures:
        return fixtures, filename

    matrix_teams = []
    for pot in CL_TEAMS:
        for team in pot:
            matrix_teams.append(
                {
                    team: {
                        "home":0,
                        "away":0,
                        "pot1":0,
                        "pot2":0,
                        "pot3":0,
                        "pot4":0,
                    }
                }
            )

    fixtures = generate_unique_fixtures(list(range(1, 37)), 8, 18)

    for rounds in fixtures:
        uniq_teams = []
        round_num =0
        for game in rounds:
            round_num = game[0]
            matrix_teams[game[1]-1][game[1]]["home"] = matrix_teams[game[1]-1][game[1]]["home"]+ 1
            matrix_teams[game[2]-1][game[2]]["away"] = matrix_teams[game[2]-1][game[2]]["away"]+1
            p = pot_for_team(game[2])
            pot_index="pot{}".format(p+1)
            matrix_teams[game[1]-1][game[1]][pot_index] = matrix_teams[game[1]-1][game[1]][pot_index] +1
            if matrix_teams[game[1]-1][game[1]][pot_index]>2:
                print("more than 2 games against {} for team {}".format(pot_index,game[1]))    
            p = pot_for_team(game[1])
            pot_index="pot{}".format(p+1)
            matrix_teams[game[2]-1][game[2]][pot_index] = matrix_teams[game[2]-1][game[2]][pot_index] +1
            if matrix_teams[game[2]-1][game[2]][pot_index]>2:
                print("more than 2 games against {} for team {}".format(pot_index,game[2])) 
            if game[1] not in uniq_teams: 
                uniq_teams.append(game[1])
            if game[2] not in uniq_teams: 
                uniq_teams.append(game[2])
            if matrix_teams[game[1]-1][game[1]]["home"] >4: 
                print("error more 4 home  games")
            if matrix_teams[game[2]-1][game[2]]["away"]>4:
                print("error more 4 away  games")
        if not len(uniq_teams) == 36:
            print("error uniq teams round {}".round_num)
    save_fixtures_to_file(fixtures, filename)
        
    return fixtures, filename
   

# Function to load and resize flag
def get_flag_image(country_code, flag_size=(100, 100)):
    # Create cache key from country_code
    cache_key = f'flag_image_{country_code}'
    
    # Try to get from cache first
    cached_image = cache.get(cache_key)
    if cached_image:
        return Image.open(BytesIO(cached_image)).resize(flag_size)
    
    try:
        url = f"https://sokker.org/static/pic/flags/{country_code}.svg"  # adjust URL as needed
        response = requests.get(url)
        response.raise_for_status()
        
        if response.headers.get('content-type') == 'image/svg+xml':
            png_data = cairosvg.svg2png(bytestring=response.content)
            image = Image.open(BytesIO(png_data))
        else:
            image = Image.open(BytesIO(response.content))
        
        image = image.convert('RGBA')
        image = image.resize(flag_size)  # Resize to flag_size
        
        # Cache the image
        img_byte_array = BytesIO()
        image.save(img_byte_array, format='PNG')
        cache.set(cache_key, img_byte_array.getvalue(), timeout=86400)  # Cache for 24 hours
        
        return image
        
    except Exception as e:
        print(f"Error processing image for country {country_code}: {e}")
        return None

COLORS = {
    'header': '#dc3545',  # Blue
    'row_even': 'lightblue',  # Light gray
    'row_odd': '#38A1F3',
    'highlight': '#ffd700',  # Gold for special rows
    'promotion': '#38A1F3',  # rgb(56, 161, 243)
    'relegation': '#dc3545',  # Light red
    'normal': '#28a745'
}
    # Draw table borders and header
def draw_cell(draw, font, x, y, width, height, text, bg_color='white', text_color='white'):
    # Draw cell with background color
    draw.rectangle([x, y, x + width, y + height], fill=bg_color, outline='black')
    
    # Draw text centered in cell
    text_width = draw.textlength(str(text), font=font)
    text_x = x + (width - text_width) // 2
    text_y = y + (height - font.size) // 2
    
    # Choose text color based on background brightness
    draw.text((text_x, text_y), str(text), fill=text_color, font=font)

def create_standings_table_image(standings, title, title_font):
    # Define dimensions and styling
    padding = 20
    title_padding = 20
    cell_padding = 10
    row_height = 40
    col_widths = {
        'pos': 50,      # Position
        'country': 50,
        'team': 300,    # Team name
        'games': 60,    # Games played
        'wins': 60,     # Wins
        'draws': 60,    # Draws
        'lost': 60,     # Losses
        'gd': 100,       # Goal difference
        'pts': 60       # Points
    }
    
    # Calculate total width and height
    width = sum(col_widths.values()) + (padding * 2)
    height = (len(standings) + 1) * row_height + (padding * 2) + title_padding + title_font.size  # +1 for header
    
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Load font
    font_path = fm.findfont(fm.FontProperties())
    font = ImageFont.truetype(font_path, 26)
    title_font = ImageFont.truetype(font_path, 30)

    # Draw title
    draw.rectangle([padding, padding, width - padding, padding + title_font.size + title_padding], fill='white')
    draw.text((padding, title_padding), title, fill='black', font=title_font)
    
    # Draw header
    headers = ['Pos', '', 'Team', 'P', 'W', 'D', 'L', 'GD', 'Pts']
    x = padding
    y = title_padding + title_font.size + padding
    
    for header, width in zip(headers, col_widths.values()):
        draw_cell(draw, font, x, y, width, row_height, header, bg_color=COLORS['header'], text_color='white')  # Blue header
        x += width
    
    # Draw data rows
    for idx, team in enumerate(standings, 1):
        x = padding
        y = padding + (idx * row_height) + title_font.size + title_padding  
        
        # Alternate row colors
        if team['promotion']:
            row_bg = COLORS['promotion']
        elif team['relegation']:
            row_bg = COLORS['relegation']
        else:
            row_bg = COLORS['normal']
        
        # Position
        draw_cell(draw, font, x, y, col_widths['pos'], row_height, team['position'], row_bg, text_color='white')
        x += col_widths['pos']
        
        flag_size = (30, 20)
        flag = get_flag_image(team["country"], flag_size)
        # Country
     
        draw_cell(draw, font, x, y, col_widths['country'], row_height, "", row_bg, text_color='white')
        
        if flag:
            img.paste(flag, (x+10, y+10))
        x += col_widths['country']
        
        # Team name
        draw_cell(draw, font, x, y, col_widths['team'], row_height, team['name'], row_bg, text_color='white')
        x += col_widths['team']
        
        # Games played
        draw_cell(draw, font, x, y, col_widths['games'], row_height, team['games'], row_bg, text_color='white')
        x += col_widths['games']
        
        # Wins
        draw_cell(draw, font, x, y, col_widths['wins'], row_height, team['wins'], row_bg, text_color='white')
        x += col_widths['wins']
        
        # Draws
        draw_cell(draw, font, x, y, col_widths['draws'], row_height, team['draw'], row_bg, text_color='white')
        x += col_widths['draws']
        
        # Losses
        draw_cell(draw, font, x, y, col_widths['lost'], row_height, team['lost'], row_bg, text_color='white')
        x += col_widths['lost']
        
        # Goal difference
        draw_cell(draw, font, x, y, col_widths['gd'], row_height, team['gd'], row_bg, text_color='white')
        x += col_widths['gd']
        
        # Points
        draw_cell(draw, font, x, y, col_widths['pts'], row_height, team['pts'], row_bg, text_color='white')
    
    # Convert to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    
    return HttpResponse(img_byte_array.getvalue(), content_type='image/png')
import requests
import os
from datetime import datetime


def get_season_week(season_data):
    today = datetime.now().date()
    start_date = datetime.strptime(season_data['start']['date']['value'], "%Y-%m-%d").date()
    end_date = datetime.strptime(season_data['end']['date']['value'], "%Y-%m-%d").date()
    weeks_difference = ((today - start_date).days) // 7
    days_difference = ((today - start_date).days) % 7
    
    # Calculate remaining Wednesdays
    remaining_days = (end_date - today).days
    # Get current weekday (0 = Monday, ..., 6 = Sunday)
    current_weekday = today.weekday()
    # Wednesday is weekday 2
    days_until_next_wednesday = (2 - current_weekday) % 7
    
    # If today is Wednesday, include it in the count
    if current_weekday == 2:
        remaining_wednesdays = (remaining_days + days_until_next_wednesday) // 7 + 1
    else:
        remaining_wednesdays = (remaining_days + days_until_next_wednesday) // 7
    
    return weeks_difference, 7-days_difference, remaining_wednesdays

# https://sokker.org/apidoc.html
def auth_sokker():
    headers = {"accept": "application/json"}
    username = os.getenv("SOKKER_USER_NAME", None)
    password = os.getenv("SOKKER_PASSWORD", None)
    if not username or not password:
        return False
    data = {"login": username, "password": password, "remember": True}
    url = "https://sokker.org/api/auth/login"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # Extract the 'Set-Cookie' header from the response
        cookies = response.cookies.get_dict()
        # Convert cookies dictionary into a cookie string
        cookie_string = "; ".join([f"{key}={value}" for key, value in cookies.items()])
        return cookie_string
    return False


def get_sokker_transfers(cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/transfer?filter[nationality]=54&filter[limit]=10000"
    # Send GET request
    
    return requests.get(url, headers=headers)


def get_sokker_player_transfer_data(player_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/player/{player_id}/transfer"
    print("player id : " + str(player_id))
    # Send GET request
    
    return requests.get(url, headers=headers)

def get_sokker_player_data(sokker_id):
    headers = {"accept": "application/json"}
    url = f"https://sokker.org/api/player/{sokker_id}"
    print("sokker id" ": " + str(sokker_id))
    # Send GET request
    return requests.get(url, headers=headers)


def get_sokker_team_data(team_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/team/{team_id}"
    print("team id : " + str(team_id))
    # Send GET request
    return requests.get(url, headers=headers)

def get_sokker_match_lineup_data(match_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/match/{match_id}/lineup"
    print("match id : " + str(match_id))
    # Send GET request
    
    return requests.get(url, headers=headers)



def get_sokker_match_stats_data(match_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/match/{match_id}/stats"
    print("match id : " + str(match_id))
    # Send GET request
    
    return requests.get(url, headers=headers)

def get_sokker_match_data(match_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/match/{match_id}"
    print("match id : " + str(match_id))
    # Send GET request
    
    return requests.get(url, headers=headers)


def get_sokker_match_data(match_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/match/{match_id}"
    print("match id : " + str(match_id))
    # Send GET request
    
    return requests.get(url, headers=headers)

def get_sokker_team_match_data(team_id, season, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/team/{team_id}/match?filter[season]={season}"
    print("team id : " + str(team_id))
    # Send GET request
    data = {}
    
    return requests.get(url, headers=headers, json=data)

def get_sokker_seasons(cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/seasons"
    return requests.get(url, headers=headers)

def get_sokker_season_data(season_id, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/season/{season_id}"
    return requests.get(url, headers=headers)


def get_sokker_team_match_data_arcade(team_id, season, cookie):
    headers = {
        "accept": "application/json",
        "Cookie": cookie,
    }
    url = f"https://sokker.org/api/league/51530/match?filter[team]={team_id}&filter[season]={season}&filter[limit]=200"
    # Send GET request
    data = {}
    
    return requests.get(url, headers=headers, json=data)



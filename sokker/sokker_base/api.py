import requests
import os


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

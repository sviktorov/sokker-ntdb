import os
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def auth_footballarena():
    headers = {"accept": "application/json"}
    username = os.getenv("FOOTBALLARENA_USER_NAME", None)
    password = os.getenv("FOOTBALLARENA_PASSWORD", None)

    if not username or not password:
        return False
    data = {
        "nick": username,
        "psw": password,
        "login": "Enter", 
        "auth": "on"
    }
    url = "https://www.footballarena.org/login.php"
    session = requests.Session() 
    response = session.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Cookies after login: {session.cookies.get_dict()}")

        return session
    return False


def fa_players_team(session, team_id):
    url = f"https://www.footballarena.org/?goto=team-player&idteam={team_id}"

    response = session.get(url)
    print(session.cookies)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div')

def get_page_content(url, session):
    # Add headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.footballarena.org/'
    }
    
    # Make the request with the session
    response = session.get(url, headers=headers)
    
    # Check if we're still logged in
    if 'login.php' in response.url:
        print("Session expired, need to re-login")
        return None
        
    return response.text

#
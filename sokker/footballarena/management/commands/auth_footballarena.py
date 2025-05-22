# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from footballarena.api import auth_footballarena, get_page_content

class Command(BaseCommand):
    help = 'Authenticate to FootballArena'

    def handle(self, *args, **kwargs):
        session = auth_footballarena()
         
        html_content = get_page_content('https://www.footballarena.org/?goto=team-player&idteam=38325', session)
        
        print(html_content)

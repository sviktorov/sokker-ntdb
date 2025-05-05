# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from sokker_base.api import auth_sokker, get_sokker_team_trophies, get_sokker_team_data
from sokker_base.models import TeamTrophies, Country, Team

class Command(BaseCommand):
    help = _("Fetch trophies")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--team_id", type=str, help="ID of the team to fetch trophies for."
        )

    def handle(self, *args, **options):
        team_id = options.get("team_id")
        if not team_id:
            self.stdout.write(self.style.ERROR("No team_id provided"))
            return
        cookie = auth_sokker()
        team_data = get_sokker_team_data(team_id, cookie).json()
        country_code = team_data['country']['code']
        country = Country.objects.filter(code=country_code).first()
        if not country:
            self.stdout.write(self.style.ERROR("Country not found"))
            return
        team = Team.objects.filter(id=team_id).first()
        if not team:
            self.stdout.write(self.style.ERROR("Team not found"))
            return
        responese = get_sokker_team_trophies(team_id, cookie).json()
 
        trophies = responese['trophies']
        for trophy in trophies:
            team_trophy = TeamTrophies.objects.filter(team=team, country=country, trophy_type=trophy['type'], position=trophy['position'], level=trophy['level']).first()

            if not team_trophy: 
                team_trophy = TeamTrophies(team=team, country=country, trophy_type=trophy['type'], position=trophy['position'], level=trophy['level'])
                team_trophy.occurrences = trophy['occurrences']
                team_trophy.save()
            else:
                team_trophy.occurrences = trophy['occurrences']
                team_trophy.save()
      


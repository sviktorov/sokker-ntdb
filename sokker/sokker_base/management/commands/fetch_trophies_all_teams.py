# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from sokker_base.models import Team, Country
from django.core.management import call_command
class Command(BaseCommand):
    help = _("Fetch trophies")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--country_id", type=str, help="ID of the country to fetch trophies for."
        )

    def handle(self, *args, **options):
        country_id = options.get("country_id")
        if not country_id:
            self.stdout.write(self.style.ERROR("No country_id provided"))
            return
        country = Country.objects.filter(code=country_id).first()
        if not country:
            self.stdout.write(self.style.ERROR("Country not found"))
            return
        
        teams = Team.objects.filter(country=country)
        for team in teams:
            self.stdout.write(self.style.SUCCESS(f"Fetching trophies for team {team.name}"))
            response = call_command('fetch_trophies', team_id=team.id)
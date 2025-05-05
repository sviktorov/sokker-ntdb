# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from sokker_base.models import Team, Country
from django.core.management import call_command


class Command(BaseCommand):
    help = _("Fetch standings for all seasons")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--country_id", type=int, help="ID of the country to fetch standings for."
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
        
        seasons = range(1, 65)
        for season in seasons:
            response = call_command('fetch_leguage_tables', country_id=country.code, season_id=season, league_id=7095)
    
        
       
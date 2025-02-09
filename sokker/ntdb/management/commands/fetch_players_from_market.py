# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import Player, PointsRequirementsCountry
from sokker_base.api import auth_sokker, get_sokker_transfers
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = "Fetch Players from Market"

    def add_arguments(self, parser):
        parser.add_argument(
            '--country-code',
            type=str,
            help=_('Filter players by country code (e.g., 54)'),
            required=True,
        )

    def handle(self, *args, **kwargs):
        country_code = kwargs['country_code'].upper()
        cookie = auth_sokker()
        transfers = get_sokker_transfers(cookie).json()
        for transfer in transfers['transfers']:
            player_country_code = transfer['player']['info']['country']['code']
            if str(player_country_code) == str(country_code):
                characteristics = transfer['player']['characteristics']
                age = characteristics['age']
                req_age = age
                if req_age > 28:
                    req_age = 28
                req = PointsRequirementsCountry.objects.filter(
                    country__code=country_code, age=req_age
                ).first()
                
                sokker_id = transfer['player']['id']
                #print(transfer['player'])
                skills = transfer['player']['info']['skills']    

                player = Player.objects.filter(sokker_id=sokker_id).first()
                if player:
                   print(player.name, player.surname, "Update")
                else:
                    player = Player()
        
                player.sokker_id = sokker_id
                player.countryid = country_code
                player.age = age
                player.name = transfer['player']['info']['name']['name']
                player.surname = transfer['player']['info']['name']['surname']
                player.skilldefending = skills['defending']
                player.skillstamina = skills['stamina']
                player.skillkeeper = skills['keeper']
                player.skillplaymaking = skills['playmaking']
                player.skillpassing = skills['passing']
                player.skilltechnique = skills['technique']
                player.skilldefending = skills['defending']
                player.skillscoring = skills['striker']
                player.skillpace = skills['pace']
                player.position = player.best_position()
                player.date = datetime.now().strftime("%Y-%m-%d")

                if req is not None and (
                    Decimal(player.calculate_att_points()) >= req.att_points
                    or Decimal(player.calculate_def_points()) >= req.def_points
                    or Decimal(player.calculate_mid_points()) >= req.mid_points
                    or Decimal(player.calculate_gk_points()) >= req.gk_points
                ):
                    player.save()
                else:
                    print(player.name, player.surname, "Not saved do not meet requirements")

                

        print(_("Script completed"))

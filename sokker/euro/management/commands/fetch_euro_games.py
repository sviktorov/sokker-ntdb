# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import Game, Cup
from sokker_base.api import auth_sokker, get_sokker_seasons, get_sokker_team_match_data
from datetime import datetime, timedelta
from django.utils import timezone
from euro.utils import format_round_date

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
        # Now you can use the c_id in your logic
        self.stdout.write(self.style.SUCCESS(f"Processing cup with ID: {c_id}"))
        try:
            cup = Cup.objects.get(pk=int(c_id))
            self.stdout.write(self.style.SUCCESS(f"Cup found: {cup.c_name}"))

            # Perform any logic you need with the `cup` object here

        except Cup.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Cup with ID {c_id} does not exist"))
            return
        if cup.c_status == "ready":
            cookie = auth_sokker()
            today_date = datetime.now().date()
            today_date_str = today_date.strftime("%Y-%m-%d")
            # Add debug prints
            print("Server timezone:", timezone.get_current_timezone())
            print("Current time (with TZ):", timezone.now())
            print("Today date:", today_date)
            print("Today date (str):", today_date_str)
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)
            print("Cup start:", cup.c_start_date.strftime("%Y-%m-%d"))
            start_date = cup.c_start_date.strftime("%Y-%m-%d")
            seasons = get_sokker_seasons(cookie).json()
            season_ids = []
            for season in seasons:
                season_start_date = season["start"]["date"]["value"]
                season_end_date = season["end"]["date"]["value"]
                if season_start_date < start_date and season_end_date > start_date:
                    season_id = season["season"]
                    season_ids.append(season_id)
                    continue

            
            # Convert season_ids to comma-separated string
            season_ids_str = ','.join(str(id) for id in season_ids)

            games = Game.objects.filter(
                c_id=cup.pk
            ).exclude(g_status__in=["DN", "REP", "ADJ", "yes"]).order_by("cup_round")

            for game in games:
                print(game.cup_round)
                
                data = get_sokker_team_match_data(game.t_id_h.t_sokker_id, season_ids_str, cookie).json()
                matches = data["matches"]
                for match in matches:
                    match_id = match["id"]
                    game_date = format_round_date(int(game.cup_round), cup.c_start_date, "%Y-%m-%d")
                    match_date = match["time"]["gameDay"]["date"]["value"]
                    if not game_date == match_date:
                        continue
                    was_played = match["time"]["wasPlayed"]
                    game_home_id = int(game.t_id_h.t_sokker_id)
                    game_away_id = int(game.t_id_v.t_sokker_id)
                    match_home_id = int(match["home"]["id"]) 
                    match_away_id = int(match["away"]["id"])
                    if (game_home_id == match_home_id or game_home_id == match_away_id) and (game_away_id == match_home_id or game_away_id == match_away_id):
                        
                        score = match['score']
                        if was_played:
                            game.g_status = "yes"
                        else:
                            game.g_status = "arranged"
                        match_score_home = score["home"]
                        match_score_away = score["away"]
               
                        if game_home_id == match_home_id:
                            game.goals_home = match_score_home
                            game.goals_away = match_score_away
                        else:
                            game.goals_home = match_score_away
                            game.goals_away = match_score_home
                        game.matchID = match_id
                        game.save()
                        print(game.g_status, game)
                        break
        print("end script")



                  



           

           
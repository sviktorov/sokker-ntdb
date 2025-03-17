# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import Game, Cup
from sokker_base.api import auth_sokker, get_sokker_seasons, get_sokker_team_match_data_arcade, get_sokker_match_lineup_data
from datetime import datetime
from arcades.utils import get_next_monday_or_saturday, get_next_day, get_previous_day, get_next_thursday
from django.utils import timezone

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
            cup = Cup.objects.get(id=c_id)
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
            # Check if today is Thursday
            is_thursday = today_date.weekday() == 3  # 3 represents Thursday (0 = Monday, 6 = Sunday)
            is_monday = today_date.weekday() == 0  # 0 represents Monday (0 = Monday, 6 = Sunday)
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)
            round_range = range(1, 22)
            round_date = {}
            start_date=cup.c_start_date.strftime("%Y-%m-%d")
            for round in round_range:
                if round == 1:
                    round_date[str(round)] = start_date
                else:
                    round_date[str(round)] = get_next_monday_or_saturday(round_date[str(round - 1)]).strftime("%Y-%m-%d")
            end_date = round_date[str(21)]
            seasons = get_sokker_seasons(cookie).json()
            season_ids = []
            for season in seasons:
                season_start_date = season["start"]["date"]["value"]
                season_end_date = season["end"]["date"]["value"]
                if season_start_date < start_date and season_end_date > start_date:
                    season_id = season["season"]
                    season_ids.append(season_id)
                    continue
                if season_end_date > end_date:
                    season_id = season["season"]
                    season_ids.append(season_id)
                    continue
            
            # Convert season_ids to comma-separated string
            season_ids_str = ','.join(str(id) for id in season_ids)

            games = Game.objects.filter(
                c_id=cup
            ).exclude(g_status__in=["DN", "REP", "ADJ", "yes"]).order_by("cup_round")

            for game in games:
                print(game.id, game.t_id_h.id, game.t_id_v.id, game.cup_round)
                data = get_sokker_team_match_data_arcade(game.t_id_h.id, season_ids_str, cookie).json()
                round = str(game.cup_round)
                if 'matches' not in data:
                    print(f"No matches found in data for game {game.id}. Data received:", data)
                    continue
                # print(round_date[round])
                
                # Add check for day difference
                round_date_obj = datetime.strptime(round_date[round], "%Y-%m-%d").date()
                days_difference = (round_date_obj - today_date).days
                # print(f"Days until round {round}: {days_difference}")
                
                # Skip if the round date is more than 7 days away
                if days_difference > 7:
                    print(f"Skipping round {round} as it's more than 7 days away")
                    break

                for match in data["matches"]:
                    was_played = match["time"]["wasPlayed"]

                    home_team_id = match["home"]["id"]
                    away_team_id = match["away"]["id"]
                    # print(was_played, home_team_id, away_team_id, game.t_id_h.id, game.t_id_v.id)
                    flag = False
                    # in groups stage home away can be reversed
                    if (str(home_team_id) == str(game.t_id_h.id) or str(away_team_id) == str(game.t_id_h.id)) and \
                       (str(home_team_id) == str(game.t_id_v.id) or str(away_team_id) == str(game.t_id_v.id)) and \
                       (int(game.cup_round) < 9 and int(game.cup_round) > 0):
                        flag = True
                        if str(home_team_id) == str(game.t_id_h.id):
                            home_match = True
                            home_goal = match["score"]["home"]
                            away_goal = match["score"]["away"]
                        else:
                            home_goal = match["score"]["away"]
                            away_goal = match["score"]["home"]
                            home_match = False
                    if (int(game.cup_round) > 8) and (str(home_team_id) == str(game.t_id_h.id) and str(away_team_id) == str(game.t_id_v.id)):
                        flag = True
                        home_goal = match["score"]["home"]

                        away_goal = match["score"]["away"]

                        home_match = True
                    if not flag:
                        continue
                    time = match["time"]["time"]["dateTime"]
                    day = time[:10]
                    # cover case when game is arranged after midnight sokker time
                    next_day = get_next_day(day)
                    previous_day = get_previous_day(day)
                    next_thursday = get_next_thursday(day).strftime("%Y-%m-%d")
                    next_thursday_day = get_next_day(next_thursday)
                    next_thursday_from_today = get_next_thursday(today_date_str).strftime("%Y-%m-%d")
                    next_thursday_from_today_day = get_next_day(next_thursday_from_today)
                    next_thursday_from_round_day = get_next_day(round_date[round])
                    
                    possible_days = [round_date[round], next_day, next_thursday, next_thursday_day, next_thursday_from_today, next_thursday_from_today_day, next_thursday_from_round_day]
                    yesterday = get_previous_day(today_date_str)
                    possible_days.append(yesterday)
                    possible_days.append(today_date_str)
                    possible_days.append(previous_day)
                    possible_days.append(today_date_str)


                    if day in possible_days  or match["id"] == game.matchID:
                        if was_played:  
                            if home_goal is not None and away_goal is not None:
                                game.g_status = "yes"
                            else:
                                game.g_status = "arranged"
                            if home_goal is not None:
                                game.goals_home = int(home_goal)
                            if away_goal is not None:
                                game.goals_away = int(away_goal)
                        else:
                            game.g_status = "arranged"
                        game.matchID = match["id"]
                        print("save")
                        print("was played", was_played)
                        print("result",home_goal, away_goal)
                        game.save()
                        print(game.id, game.g_status,game.t_id_h, game.t_id_v, game.goals_home, game.goals_away)
                        break

               
            
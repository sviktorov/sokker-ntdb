# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from arcades.models import Game, Cup, RankGroups
from arcades.utils import PLAYOFF_FIXTURES_CL

from sokker_base.models import Team


class Command(BaseCommand):
    help = _("Cup fixtures CL")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--c_id", type=str, help="ID of the cup to perform the draw on."
        )

    def get_winner_in_playoff(self, playoff_position, cup):
        games = Game.objects.filter(playoff_position=playoff_position, c_id=cup).order_by("pk")
        home_team = None
        away_team = None
        home_score = 0
        away_score = 0
        counter = 0
        for game in games:
            print(game)
            counter += 1
            if game.g_status == "yes" or game.g_status == "ADJ":
                if counter == 1:
                    home_team = game.t_id_h
                    away_team = game.t_id_v
                    home_score = game.goals_home
                    away_score = game.goals_away
                if  counter == 2:
                    home_score+= game.goals_away
                    away_score+= game.goals_home
                    if home_score > away_score:
                        return home_team
                    if away_score > home_score:
                        return away_team
                if counter == 3:
                    if game.goals_home > game.goals_away:
                        return game.t_id_h
                    if game.goals_away > game.goals_home:
                        return game.t_id_v
                    return None
        return None
    
    def find_teams_in_playoff(self, game_fixture, ranking_teams, cup):
        round_number = game_fixture[0]
        home_team = game_fixture[1]
        away_team = game_fixture[2]
        if isinstance(home_team, str):
            home_team = self.get_winner_in_playoff(home_team, cup)
        else:
            home_team = ranking_teams[int(home_team)-1]

        if isinstance(away_team, str):
            away_team = self.get_winner_in_playoff(away_team, cup)
        else:
            away_team = ranking_teams[int(away_team)-1]
        return home_team, away_team

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

        check = RankGroups.objects.filter(c_id=cup, g_id=1, games= "8")
        can_do_playoff = check.count() == 36
        if not can_do_playoff:
            self.stdout.write(self.style.ERROR("Not all games are played from group stage"))
            return

        if cup.c_active and cup.is_cl:
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)
            ranking_teams = RankGroups.objects.filter(c_id=cup, g_id=1).order_by("-points", "-gdif", "-gscored")
            for game_fixture in PLAYOFF_FIXTURES_CL:
                round_number = game_fixture[0]
                playoff_position = game_fixture[3]
                if int(round_number) > 9:
                    home_team, away_team = self.find_teams_in_playoff(game_fixture, ranking_teams, cup)
                    if home_team is None or away_team is None:
                        self.stdout.write(self.style.ERROR(f"Game {playoff_position} is not ready to arrange {home_team} vs {away_team}"))
                        continue
                    if isinstance(home_team, Team):
                        home_team = home_team
                    else:
                        home_team = home_team.t_id
                    if isinstance(away_team, Team):
                        away_team = away_team
                    else:
                        away_team = away_team.t_id
                else:
                    home_team = ranking_teams[int(game_fixture[1])-1]
                    home_team = home_team.t_id
                    away_team = ranking_teams[int(game_fixture[2])-1]
                    away_team = away_team.t_id
        
                print(f"Creating game with home_team_id: {home_team}, away_team_id: {away_team}")
                is_game_played = Game.objects.filter(
                    t_id_h=home_team, 
                    t_id_v=away_team, 
                    c_id=cup, 
                    playoff_position=playoff_position
                ).exists()
                if is_game_played:
                    self.stdout.write(self.style.SUCCESS(f"Game {home_team} vs {away_team} is already set"))
                    continue
                # create game 1
                game = Game()
                game.t_id_h = home_team
                game.t_id_v = away_team
                game.c_id = cup
                game.cup_round = int(round_number)
                game.group_id = 0
                game.playoff_position = playoff_position
                game.save()

                # create game 2
                game = Game()
                game.t_id_h = away_team
                game.t_id_v = home_team
                game.c_id = cup
                game.cup_round = int(round_number)
                game.group_id = 0
                game.g_status = ""
                game.playoff_position = playoff_position
                game.save()
            cup.c_draw_status = "ready"
            cup.c_status = "ready"
            cup.save()

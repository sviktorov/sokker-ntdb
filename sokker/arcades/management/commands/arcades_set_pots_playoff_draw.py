from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from arcades.models import Cup, PlayoffPots, RankGroups
from sokker_base.models import Team
class Command(BaseCommand):
    help = _("Set pots for playoff draw")

    def add_arguments(self, parser):
        # Add c_id argument here
        parser.add_argument(
            "--c_id", type=str, help="ID of the cup to perform the draw on."
        )

    def handle(self, *args, **options):
        c_id = options.get("c_id")
        cup = Cup.objects.get(id=c_id)
        teams_in_playoffs = int(cup.c_g_winners)
        pot_size = int(teams_in_playoffs / 2)
        total_teams = int(cup.c_teams)
        groups = int(cup.c_groups)
        group_size = int(total_teams / groups)

        pot1 = []
        pot2 = []
        pot3 = []
        pot4 = []
        pass_position = int(pot_size / groups)
        print(pass_position)
        standings = []
        for group in range(1, groups + 1):
            rank_group = RankGroups.objects.filter(c_id=cup, g_id=group).order_by("-points", "-gdif", "gscored").values_list("t_id", flat=True)
            standings.append(rank_group)
            
            if pass_position > 0:
                position = 1
                for team in rank_group:
                    if position <= pass_position:
                        pot1.append(team)
                    else:
                        break
                    position += 1
        blue_teams = []
        if len(pot1)  < pot_size:
            
            for group in standings:
                index = pass_position - 1
                if index < 0:
                    index = 0
                blue_teams.append(group[index])
        
        blue_teams = RankGroups.objects.filter(c_id=cup, t_id__in=blue_teams).order_by("-points", "-gdif", "gscored").values_list("t_id", flat=True)
        for team in blue_teams:
            if len(pot1) < pot_size:
                pot1.append(team)
            else:
                if len(pot2) < pot_size:
                    pot2.append(team)
                else:
                    break
        pass_position = pass_position + 1
        while len(pot2) < pot_size:
            for group in standings:
                if pass_position < len(group):  # Check if the position exists in the group
                    pot2.append(group[pass_position])
            pass_position += 1
            
        
        PlayoffPots.objects.filter(c_id=cup, pot_id=1).delete()
        for team in pot1:
            team_obj = Team.objects.get(id=team)
            PlayoffPots.objects.create(c_id=cup, pot_id=1, t_id=team_obj, flow=1)

        PlayoffPots.objects.filter(c_id=cup, pot_id=2).delete()
        for team in pot2:
            team_obj = Team.objects.get(id=team)
            PlayoffPots.objects.create(c_id=cup, pot_id=2, t_id=team_obj, flow=1)


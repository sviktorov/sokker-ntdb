# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import Winners, Medals, NTTeam
from django.db.models import Q


class Command(BaseCommand):
    help = _("Update medals table")

    def handle(self, *args, **options):
        distinct_teams = (
            Winners.objects.filter(cup_id__c_flow=1).values("team_id").distinct()
        )
        Medals.objects.all().delete()
        for team in distinct_teams:

            team_object = NTTeam.objects.filter(pk=team["team_id"]).first()
            position_1 = Winners.objects.filter(
                team_id__pk=team["team_id"], position=1
            ).count()
            position_2 = Winners.objects.filter(
                team_id__pk=team["team_id"], position=2
            ).count()
            position_3 = Winners.objects.filter(
                team_id__pk=team["team_id"], position=3
            ).count()
            position_4 = Winners.objects.filter(
                team_id__pk=team["team_id"], position=4
            ).count()
            medal_object = Medals()

            medal_object.t_id = team_object
            medal_object.position_1 = position_1
            medal_object.position_2 = position_2
            medal_object.position_3 = position_3
            medal_object.position_4 = position_4
            medal_object.save()

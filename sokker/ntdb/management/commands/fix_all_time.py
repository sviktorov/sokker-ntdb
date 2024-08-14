# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import Player, ArchivePlayer
from django.db.models import Q


class Command(BaseCommand):
    help = "Fix all time age"

    def handle(self, *args, **options):
        players = Player.objects.all()
        msg = _("Player id {} set as {}")
        for player in players:
            archive = ArchivePlayer.objects.filter(sokker_id=player.sokker_id).order_by(
                "-age"
            )[:2]

            print(player.sokker_id, len(archive))
            if len(archive) == 2:
                print(archive[0].age)
                print(archive[1].age)
                if archive[0].age and archive[0].age == archive[1].age:
                    archive[1].age = archive[0].age - 1
                    archive[1].save()

                # addPlayer.save()

        print(_("Script completed"))

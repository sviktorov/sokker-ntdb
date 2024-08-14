# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import ArchivePlayer
from django.db.models import Q


class Command(BaseCommand):
    help = "Fix missing position"

    def handle(self, *args, **options):
        players = ArchivePlayer.objects.all()
        msg = _("Player id {} set as {}")
        for player in players:
            aPlayer = (
                ArchivePlayer.objects.filter(sokker_id=player.sokker_id, age=player.age)
                .order_by("-id")
                .first()
            )
            print(msg.format(player.sokker_id, player.age))
            ArchivePlayer.objects.filter(
                sokker_id=player.sokker_id, age=player.age
            ).exclude(pk=aPlayer.pk).delete()

        print(_("Script completed"))

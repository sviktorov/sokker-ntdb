# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from ntdb.models import Player
from django.db.models import Q


class Command(BaseCommand):
    help = "Fix missing position"

    def handle(self, *args, **options):
        players = Player.objects.filter(Q(position="") | Q(position__isnull=True))
        msg = _("Player id {} set as {}")
        for player in players:
            formatted_msg = msg.format(player.sokker_id, player.best_position())
            player.position = player.best_position()
            player.save()
            print(formatted_msg)
        print(_("Script completed"))

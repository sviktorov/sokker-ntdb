from arcades.utils import get_next_available_cup_date
from arcades.models import Cup
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

class Command(BaseCommand):
    help = _("Cup draw Euro")

    def add_arguments(self, parser):
        parser.add_argument(
            "--c_id", type=str, help="ID of the cup to perform the draw on."
        )

    def handle(self, *args, **options):
        c_id = options.get("c_id")
        if not c_id:
            self.stdout.write(self.style.ERROR("No c_id provided"))
        cup = Cup.objects.get(pk=c_id)
        get_next_available_cup_date(cup)

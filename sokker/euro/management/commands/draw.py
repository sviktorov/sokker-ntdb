# yourapp/management/commands/copy_players_to_archive.py
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from euro.models import CupDraw, Cup, CupTeams
from django.utils import timezone
from datetime import timedelta
import random


def remove_element_by_value(lst, value):
    """Removes the first occurrence of the specified value from the list.

    Args:
        lst: The list to modify.
        value: The value to remove.

    Returns:
        None
    """

    try:
        lst.remove(value)
    except ValueError:
        pass  # Value not found in the list


class Command(BaseCommand):
    help = _("Cup draw Euro")

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

        if cup.c_draw_status == "ready":
            print("Number of teams:", cup.c_teams)
            print("Number of groups:", cup.c_groups)

            pot_iterations = int(cup.c_teams / cup.c_groups)
            CupTeams.objects.filter(c_id=cup).delete()
            for i in range(1, pot_iterations + 1):
                group_numbers = list(range(1, cup.c_groups + 1))
                pots = CupDraw.objects.filter(c_id=cup, g_id=i).order_by("g_id")
                for team in pots:
                    # Randomly shuffle the group_numbers
                    random.shuffle(group_numbers)
                    print(group_numbers)
                    ct = CupTeams()
                    ct.c_id = cup
                    ct.g_id = group_numbers[0]
                    ct.t_id = team.t_id
                    ct.save()
                    remove_element_by_value(group_numbers, group_numbers[0])
            cup.c_draw_status = "done"
            cup.c_status = "fixtures"
            cup.save()

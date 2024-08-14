from .models import ArchivePlayer, Player
from django_filters import FilterSet, NumberFilter, widgets
from django.utils.translation import gettext_lazy as _


class ArchivePlayerAgeFilter(FilterSet):
    age = NumberFilter(
        field_name="age",
        help_text=_("Filter records based on your numeric field."),
        # initial={"min": 16, "max": 50},
        distinct=True,
        exclude=False,
        error_messages={
            "invalid": "Please enter a valid number.",
            "required": "This field is required.",
        },
    )

    class Meta:
        model = ArchivePlayer
        fields = ["age"]


class PlayerAgeFilter(FilterSet):
    age = NumberFilter(
        field_name="age",
        help_text=_("Filter records based on your numeric field."),
        # initial={"min": 16, "max": 50},
        distinct=True,
        exclude=False,
        error_messages={
            "invalid": "Please enter a valid number.",
            "required": "This field is required.",
        },
    )

    class Meta:
        model = Player
        fields = ["age"]

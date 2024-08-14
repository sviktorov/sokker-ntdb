from .models import Player
from sokker_base.models import Country
from django import forms


class PlayerAdminForm(forms.ModelForm):
    CHOICES_POSITION = [
        ("GK", "GK"),
        ("DEF", "DEF"),
        ("MID", "MID"),
        ("ATT", "ATT"),
    ]
    position = forms.ChoiceField(choices=CHOICES_POSITION)
    countryid = forms.ChoiceField(
        choices=[(country.code, country.name) for country in Country.objects.all()]
    )

    class Meta:
        model = Player
        fields = "__all__"

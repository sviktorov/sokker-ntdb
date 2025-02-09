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

class PlayerManualUpdateForm(forms.Form):
    pid = forms.IntegerField()
    player_data = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 100}))


class PlayerForm(forms.ModelForm):
    player_data = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Player
        fields = ['sokker_id', 'name', 'surname', 'skillstamina', 'skillkeeper', 'skillpace', 'skilldefending', 'skilltechnique', 'skillplaymaking', 'skillpassing', 'skillscoring']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields read-only
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True

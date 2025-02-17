from django import forms


class PlayerPredictionForm(forms.Form):
    training_sessions = forms.IntegerField(
        label="Training Sessions", 
        required=False,
        widget=forms.HiddenInput()
    )
    current_age = forms.IntegerField(label="Current Age")
    target_age = forms.IntegerField(label="Target Age")
    talent = forms.FloatField(label="Talent", min_value=3)
    player_data = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 100}), required=False)  
    extra_trainings = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 100}), required=False)
    # training_distribution = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 100}), required=False)

class FetchTacticDataForm(forms.Form):
    id = forms.CharField(label="ID", max_length=100)


class PostTacticDataForm(forms.Form):
    id = forms.CharField(label="ID", max_length=100)
    code = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "cols": 100}), label="Code"
    )


class SwapPositionsForm(forms.Form):
    input_code = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "cols": 100}), label="Input Code"
    )
    POSITION_CHOICES = [(i, i) for i in range(2, 12)]
    position1 = forms.ChoiceField(choices=POSITION_CHOICES, label="Position 1")
    position2 = forms.ChoiceField(choices=POSITION_CHOICES, label="Position 2")
    output_code = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "cols": 100}),
        label="Output Code",
    )

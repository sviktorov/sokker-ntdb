from django import forms


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

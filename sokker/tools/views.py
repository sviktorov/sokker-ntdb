import requests
from django.shortcuts import render
from .forms import FetchTacticDataForm, PostTacticDataForm, SwapPositionsForm, PlayerPredictionForm
from ntdb.forms import PlayerManualUpdateForm, PlayerForm
import re
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from sokker_base.api import get_sokker_seasons, auth_sokker, get_season_week 
from ntdb.utils import extract_skill_value, INITIAL_PHARSE_PLAYER
from django import forms
PLAYER_SLOT = 70


def transform_tactic_positions(tact, pos1, pos2):
    if pos1 > 1 and pos2 > 1 and pos1 != pos2 and pos1 <= 11 and pos2 <= 11:
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1

        end1 = (pos1 - 1) * PLAYER_SLOT - 1
        start1 = (pos1 - 2) * PLAYER_SLOT
        end2 = (pos2 - 1) * PLAYER_SLOT - 1
        start2 = (pos2 - 2) * PLAYER_SLOT
        code_pos1 = tact[start1:end1]
        code_pos2 = tact[start2:end2]
        tact_new = (
            tact[:start1] + code_pos2 + tact[end1:start2] + code_pos1 + tact[end2:]
        )

        return tact_new
    return tact


def fetch_tactics_data(request):
    response_data = None
    url_save = None
    url_fetch = None
    if request.method == "POST":
        form = FetchTacticDataForm(request.POST)
        form2 = PostTacticDataForm(request.POST)
        form3 = SwapPositionsForm(request.POST)
        tact_value = ""

        if "form1_submit" in request.POST:
            if form.is_valid():
                id_value = form.cleaned_data["id"]
                url_fetch = f"https://sokker.org/read_tact.php?id={id_value}/"  # Replace with your external URL
                response = requests.get(url_fetch)
                if response.status_code == 200:
                    match = re.search(r"tact=([A-Za-z0-9]+)&ok=1", response.text)
                    if match:
                        tact_value = match.group(1)
                        response_data = tact_value
                    else:
                        response_data = "No 'tact' parameter found"
                else:
                    response_data = f"Error: {response.status_code} - {response.reason}"
                form2 = PostTacticDataForm(initial={"code": tact_value})
        if "form2_submit" in request.POST:
            if form2.is_valid():
                id_value = form2.cleaned_data["id"]
                code_value = form2.cleaned_data["code"]
                url_save = f"https://sokker.org/tactedit.php?save=1&id={id_value}&tact={code_value}"
        if "form3_submit" in request.POST:
            if form3.is_valid():
                input_code = form3.cleaned_data["input_code"]
                pos1 = form3.cleaned_data["position1"]
                pos2 = form3.cleaned_data["position2"]
                output_code = transform_tactic_positions(
                    input_code, int(pos1), int(pos2)
                )
                form3 = SwapPositionsForm(
                    initial={
                        "output_code": output_code,
                        "input_code": input_code,
                        "position1": pos1,
                        "position2": pos2,
                    }
                )

    else:
        form = FetchTacticDataForm()
        form2 = PostTacticDataForm()
        form3 = SwapPositionsForm()

    return render(
        request,
        "tools/fetch_tactics_data.html",
        {
            "page_title": _("Tactics transfer"),
            "form": form,
            "response_data": response_data,
            "form2": form2,
            "url_fetch": url_fetch,
            "url": url_save,
            "form3": form3,
        },
    )


class PlayerPrediction(FormView):
    template_name = "tools/player-prediction.html"
    form_class = PlayerPredictionForm
    season_week = None
    day_week = None
    training_sessions = None
    season = None
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # Initialize season data only once
        if self.season_week is None:
            cookie = auth_sokker()
            seasons = get_sokker_seasons(cookie).json()
            season = seasons[0]
            self.season = season
            self.season_week, self.day_week, self.training_sessions = get_season_week(season)
            
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        player_form_data = None
        extra_skills_form_data = None
        if form.is_valid():
            current_age = form.cleaned_data["current_age"]
            target_age = form.cleaned_data["target_age"]
            player_data = form.cleaned_data["player_data"]
            extra_trainings = form.cleaned_data["extra_trainings"]
            #training_distribution = form.cleaned_data["training_distribution"]
            
            # Extract values for each skill
            sta = extract_skill_value(player_data, "stamina")
            kee = extract_skill_value(player_data, "keeper")
            pac = extract_skill_value(player_data, "pace")
            def_skill = extract_skill_value(player_data, "defender")
            tec = extract_skill_value(player_data, "technique")
            pla = extract_skill_value(player_data, "playmaker")
            pas = extract_skill_value(player_data, "passing")
            str_skill = extract_skill_value(player_data, "striker")

            sta_trainings = extract_skill_value(extra_trainings, "stamina")
            kee_trainings = extract_skill_value(extra_trainings, "keeper")
            pac_trainings = extract_skill_value(extra_trainings, "pace")
            def_trainings = extract_skill_value(extra_trainings, "defender")
            tec_trainings = extract_skill_value(extra_trainings, "technique")
            pla_trainings = extract_skill_value(extra_trainings, "playmaker")
            pas_trainings = extract_skill_value(extra_trainings, "passing")
            str_trainings = extract_skill_value(extra_trainings, "striker")

            
            
            age_difference = target_age - current_age
            training_sessions = self.training_sessions + (age_difference-1)*13
            # Initialize form data with skills from parameters
            player_form_data = {
                'age': current_age,
                'skillstamina': sta,
                'skillkeeper': kee,
                'skillpace': pac,
                'skilldefending': def_skill,
                'skilltechnique': tec,
                'skillplaymaking': pla,
                'skillpassing': pas,
                'skillscoring': str_skill,
                'player_data': player_data,
                'current_age': current_age,

            }
            playerForm = PlayerForm(initial=player_form_data)
            
            # Only hide fields that exist in the form
            if 'sokker_id' in playerForm.fields:
                playerForm.fields['sokker_id'].widget = forms.HiddenInput()
            
            # Always add and set age field as hidden
            if 'age' not in playerForm.fields:
                playerForm.fields['age'] = forms.IntegerField(
                    required=False,
                    widget=forms.HiddenInput()
                )
            else:
                playerForm.fields['age'].widget = forms.HiddenInput()
            
            if 'name' in playerForm.fields:
                playerForm.fields['name'].widget = forms.HiddenInput()
            if 'surname' in playerForm.fields:
                playerForm.fields['surname'].widget = forms.HiddenInput()

            # Create extra_skills form data
            extra_skills_form_data = {
                'skillstamina': sta_trainings,
                'skillkeeper': kee_trainings,
                'skillpace': pac_trainings,
                'skilldefending': def_trainings,
                'skilltechnique': tec_trainings,
                'skillplaymaking': pla_trainings,
                'skillpassing': pas_trainings,
                'skillscoring': str_trainings,
            }
            print(extra_skills_form_data)
     
            

            # Update the form's initial data
            form = self.form_class(initial={
                **form.cleaned_data,
                'training_sessions': training_sessions,
                'current_age': current_age,
            })
        else:
            playerForm = PlayerForm(initial=player_form_data)
            
            # Only hide fields that exist in the form
            if 'sokker_id' in playerForm.fields:
                playerForm.fields['sokker_id'].widget = forms.HiddenInput()
            
            # Always add and set age field as hidden
            if 'age' not in playerForm.fields:
                playerForm.fields['age'] = forms.IntegerField(
                    required=False,
                    widget=forms.HiddenInput()
                )
            else:
                playerForm.fields['age'].widget = forms.HiddenInput()
            
            if 'name' in playerForm.fields:
                playerForm.fields['name'].widget = forms.HiddenInput()
            if 'surname' in playerForm.fields:
                playerForm.fields['surname'].widget = forms.HiddenInput()

            
        
        context = self.get_context_data(form=form, playerForm=playerForm, extra_skills_form_data=extra_skills_form_data, **kwargs)
        return self.render_to_response(context)
        
    def get(self, request, *args, **kwargs):
        # Get sokker_id from URL parameters
        sokker_id = request.GET.get("sokker_id", None)
        # Initialize form with all required initial data
        initial_data = {
            'player_data': INITIAL_PHARSE_PLAYER.format("", "", "", "", "", "", "", ""),
            'extra_trainings': INITIAL_PHARSE_PLAYER.format("", "", "", "", "", "", "", ""),
            #'training_distribution': INITIAL_PHARSE_PLAYER.format("", "", "", "", "", "", "", ""),
            'current_age': None,
            'target_age': None
        }
        form = self.form_class(initial=initial_data)
        playerForm = PlayerForm()
        context = self.get_context_data(form=form, playerForm=playerForm, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Player Prediction")
        context["menu_type"] = "Tools"  
        context["season_week"] = self.season_week
        context["day_week"] = self.day_week
        context["training_sessions"] = self.training_sessions
        context["season"] = self.season
        return context




import requests
from django.shortcuts import render
from .forms import FetchTacticDataForm, PostTacticDataForm, SwapPositionsForm
import re
from django.utils.translation import gettext_lazy as _

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

from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, RankGroups, Game, Medals, RankAllTime, CupDraw, CupTeams
from .tables import RankGroupsTable
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect
import json
from collections import defaultdict
from django.core.management import call_command
from io import StringIO
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from PIL import Image, ImageDraw, ImageFont
from arcades.utils import get_flag_image, create_standings_table_image
from django.views.decorators.cache import cache_control
import io
import matplotlib.font_manager as fm
from django.views.decorators.cache import cache_page
import math

EURO_SUB_MENU = [
    {"title": _("Euros - listing"), "url": "/en/euro"},
    {"title": _("Medals"), "url": "/en/euro/medals"},
    {"title": _("Rank"), "url": "/en/euro/rank"},
]


class EuroAdminDashboard(LoginRequiredMixin, TemplateView):
    template_name = "euro/euro-admin-dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Administration Arcade")
        context["page_siblings"] = EURO_SUB_MENU
        context["menu_type"] = "ARCADES"
        return context


def CommandFormPlayerUpdate(request):
    c_id = request.GET.get("c_id")
    buffer = StringIO()
    if c_id:
        call_command("draw", c_id=str(c_id), stdout=buffer)
        # Get the output from the buffer
        command_output = buffer.getvalue()
        print(command_output)
        buffer.close()
        redirect_url = reverse("cup_draw", kwargs={"cup_id": str(c_id)})
        return HttpResponseRedirect(redirect_url)
    else:
        # If 'c_id' is not provided, you can handle the error or set a default value
        return HttpResponse("Error: c_id parameter is missing.", status=400)


class CupIndex(TemplateView):
    template_name = "euro/index.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_list = Cup.objects.all().order_by("c_flow", "-c_edition")
        context["page_title"] = _("Euro Cups")
        context["page_siblings"] = []
        context["cups"] = cup_list
        context["page_siblings"] = EURO_SUB_MENU
        context["menu_type"] = "EURO"
        return context


class CupMedals(TemplateView):
    template_name = "euro/medals.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Medals.objects.all().order_by(
            "-position_1", "-position_2", "-position_3", "-position_4"
        )
        context["page_siblings"] = EURO_SUB_MENU
        context["menu_type"] = "EURO"
        context["page_title"] = _("Medals")
        context["teams"] = teams
        return context


class CupRank(TemplateView):
    template_name = "euro/rank.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = RankAllTime.objects.filter(c_flow=1).order_by(
            "-points", "-gdif", "-gscored"
        )
        context["page_siblings"] = EURO_SUB_MENU
        context["menu_type"] = "EURO"
        context["page_title"] = _("Rank")
        context["teams"] = teams
        return context


class CupDrawTemplate(TemplateView):
    template_name = "euro/cup-draw.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        pots = CupDraw.objects.filter(c_id=cup_object).order_by("g_id")
        draw = CupTeams.objects.filter(c_id=cup_object).order_by("pk")
        menu = EURO_SUB_MENU
        group_numbers = list(range(1, cup_object.c_groups + 1))
        pot_numbers = list(range(1, int(cup_object.c_teams / cup_object.c_groups) + 1))
        # pot_iterations = int(cup.c_teams / cup.c_groups)
        draw_json = []
        group_indexes = defaultdict(int)

        for td in draw:
            group_indexes[td.g_id] += 1
            draw_json.append(
                {
                    "from": "pot_{}".format(td.t_id.t_sokker_id),
                    "to": "group_{}_{}".format(td.g_id, group_indexes[td.g_id]),
                    "sokker_id": td.t_id.t_sokker_id,
                }
            )
        context["page_siblings"] = []
        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        context["pots"] = pots
        context["group_numbers"] = group_numbers
        context["pot_numbers"] = pot_numbers
        context["col_lg_groups"] = str(int(12 / int(cup_object.c_groups)))
        context["col_lg_pots"] = str(
            int(12 / int(cup_object.c_teams / cup_object.c_groups))
        )
        context["draw"] = draw
        context["draw_json"] = json.dumps(draw_json)
        return context


class CupDetails(MultiTableMixin, TemplateView):
    template_name = "euro/cup-details.html"  # Create this template
    context_object_name = "objects"
    tables = []

    def dispatch(self, request, *args, **kwargs):
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()

        if cup_object and cup_object.c_status == "signup":
            self.template_name = "euro/cup-signup.html"  # Create this template

        if cup_object and self.tables == []:
            my_tables = []
            group_numbers = list(range(1, cup_object.c_groups + 1))
            for g_id in group_numbers:
                group = (
                    RankGroups.objects.filter(c_id=cup_object, g_id=g_id)
                    .order_by("-points", "-gdif","-gscored")
                )
                my_tables.append(
                    RankGroupsTable(group),
                )
                self.tables = my_tables

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        final = Game.objects.filter(c_id=cup_id, playoff_position="final").first()
        final_bronze = Game.objects.filter(
            c_id=cup_id, playoff_position="3/4 final"
        ).first()
        semi_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["s1", "s2"]
        ).order_by("playoff_position")

        quarter_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["q1", "q2", "q3", "q4"]
        ).order_by("playoff_position")

        eight_finals = Game.objects.filter(
            c_id=cup_id,
            playoff_position__in=[
                "e1",
                "e2",
                "e3",
                "e4",
                "e5",
                "e6",
                "e7",
                "e8",
            ],
        ).order_by("playoff_position")
        url = ""
        if cup_object:
            title = cup_object.c_name
            context["page_title"] = title
            url = reverse("cup_details", kwargs={"cup_id": str(cup_object.pk)})
        menu = EURO_SUB_MENU

        # Check if the URL already exists in the `menu`
        if not any(item["url"] == url for item in menu):
            menu.append({"title": cup_object.c_name, "url": url})
        context["final"] = final
        context["final_bronze"] = final_bronze
        context["semi_finals"] = semi_finals
        context["quarter_finals"] = quarter_finals
        context["eight_finals"] = eight_finals

        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "ARCADES"
        context["groups"] = range(1, cup_object.c_groups +1)
        return context

@cache_page(timeout=60 * 60 * 24)
def cup_round_image(request, cup_id, group_id, round_id):
    # Get default font
    font_path = fm.findfont(fm.FontProperties())
    title_font = ImageFont.truetype(font_path, 32)
    sub_title_font = ImageFont.truetype(font_path, 26)

    game_font = ImageFont.truetype(font_path, 16)

    # Get your data
    cup = Cup.objects.get(id=cup_id)
    games = Game.objects.filter(c_id=cup_id, group_id=group_id).order_by("cup_round")
    n_games = len(games)
    padding = 60
    width = 900
    height = 100 + (n_games * 30)
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw title
    draw.text((20, 10), f"{cup.c_name}", fill='black', font=title_font)
    draw.text((20, 50), f"Group {group_id} ", fill='blue', font=sub_title_font)

    # Draw games


    flag_size = (26, 17)  # Adjust size as needed
    y = 90
    for game in games:
        # Home team flag
        home_flag = get_flag_image(game.t_id_h.t_nation, flag_size)
        if home_flag:
            img.paste(home_flag, (padding, y))

        # Away team flag
        away_flag = get_flag_image(game.t_id_v.t_nation, flag_size)
        if away_flag:
            img.paste(away_flag, (width - padding - flag_size[0], y))
   
        text_home = f"{game.t_id_h.t_name}" 
        text_result = f"{game.goals_home} - {game.goals_away}".replace("None", " ")
        text_away = f"{game.t_id_v.t_name}"

        icon_color = {
            'arranged': '#ffc107',  # warning yellow
            'yes': '#28a745',      # success green
            'REP': '#ffc107',      # warning yellow
            'DN': '#dc3545',       # danger red
            'ADJ': '#28a745',      # success green
            'default': '#dc3545'   # danger red
        }
        # Draw colored circle for status
        x = 450
        font = ImageFont.truetype(font_path, 16)
        symbol_color = icon_color.get(game.g_status, icon_color['default'])
        draw.text((20, y), f"{game.cup_round}", fill='black', font=game_font)
        draw.text((100, y), text_home, fill='black', font=game_font)
        draw.text((380, y), text_result, fill='black', font=game_font)
        draw.text((500, y), text_away, fill='black', font=game_font)

        # Add small symbol inside circle based on status

        if game.g_status == 'arranged':
            draw.text((x, y), '✓', fill=symbol_color, font=font)
        elif game.g_status == 'yes':
            draw.text((x, y), '✓', fill=symbol_color, font=font)
        elif game.g_status == 'REP':
            draw.text((x, y), '↻', fill=symbol_color, font=font)
        elif game.g_status == 'DN':
            draw.text((x, y), '✕', fill=symbol_color, font=font)
        elif game.g_status == 'ADJ':
            draw.text((x, y), '⚖', fill=symbol_color, font=font)
        else:
            draw.text((x, y), '✕', fill=symbol_color, font=font)


    
        y += 30
    
    # Convert image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)
    
    # Return image
    response = HttpResponse(img_byte_array.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="cup_{cup_id}_round_{round_id}.png"'
    return response


@cache_page(timeout=60 * 60 * 24)
def cup_group_standings_image(request, cup_id, group_id):
    # Get default font
    font_path = fm.findfont(fm.FontProperties())
    title_font = ImageFont.truetype(font_path, 32)
    sub_title_font = ImageFont.truetype(font_path, 26)

    # Get your data
    cup = Cup.objects.get(id=cup_id)
    group = RankGroups.objects.filter(c_id=cup, g_id=group_id).order_by("-points", "-gdif", "-gscored")
    standings = []
    position = 1
    title = f"Group {group_id}"
    promotion_limit = cup.c_g_winners / cup.c_groups
    promotion_whole = int(promotion_limit)
    has_extra = not math.isclose(promotion_limit, promotion_whole)

    for team in group:
        promotion = False
        relegation = False

        if position <= promotion_whole:
            promotion = True
        elif has_extra and position == promotion_whole + 1:
            # This is the "neutral" position, neither promotion nor relegation
            promotion = False
            relegation = False
        else:
            relegation = True

        standings.append({
            "position": position,
            "name": team.t_id.t_name,
            "games": team.games,
            "wins": team.wins,
            "draw": team.draw,
            "lost": team.loose,
            "gd": str(team.gscored)  + " - " + str(team.grecieved),
            "pts": team.points,
            "promotion": promotion,
            "relegation": relegation,
            "country": team.t_id.t_nation
        })
        position += 1
    return create_standings_table_image(standings, title, title_font)







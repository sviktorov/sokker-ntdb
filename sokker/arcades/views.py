from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, RankGroups, Game, Medals, RankAllTime, CupCategory, CupDraw, CupTeams
from .tables import RankGroupsTable
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect
from .utils import generate_fixtures_cl, get_flag_image
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast
import json
from collections import defaultdict
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import PLAYOFF_FIXTURES_CL
from sokker_base.models import Team
from django.core.management import call_command
from django.http import HttpResponseRedirect
from io import StringIO
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io
import matplotlib.font_manager as fm
from .utils import create_standings_table_image
from django.views.decorators.cache import cache_page
from .templatetags.custom_tags_arcades import get_cup_round_date

ARCADES_SUB_MENU = [
    {"title": _("Arcade tournaments"), "url": "/en/arcades/cups"},
    {"title": _("Stat Pots"), "url": "/en/arcades/{}cl-cup/stat-pots"},
]


def pass_category_to_menu(category: CupCategory):
    menu = []
    for item in ARCADES_SUB_MENU:
        item["url"] = item["url"].format(category.slug)
        menu.append(item)
    return menu

class ArcadesAdminDashboard(LoginRequiredMixin, TemplateView):
    template_name = "arcades/arcades-admin-dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Administration Arcade")
        context["page_siblings"] = ARCADES_SUB_MENU
        context["menu_type"] = "ARCADES"
        return context


class CLFixtures(TemplateView):
    template_name = "arcades/cl_fixtures.html" 
    
    def get_context_data(self, **kwargs):
        fixtures, filename = generate_fixtures_cl()
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("CL Fixtures")
        context["page_siblings"] = []
        context["fixtures"] = fixtures
        context["filename"] = filename
        context["page_siblings"] = ARCADES_SUB_MENU
        context["menu_type"] = "ARCADES"
        return context

class CupIndex(TemplateView):
    template_name = "arcades/index.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = CupCategory.objects.all()
        page_siblings = ARCADES_SUB_MENU
        if len(page_siblings) == len(ARCADES_SUB_MENU):
            for category in categories:
                url = reverse(
                    "arcade_cup_index_category",
                    kwargs={
                        "category_slug": str(category.slug),
                    },
                )
                page_siblings.append(
                    {
                        "title": category.name,
                        "url": url
                    }
                )

        cup_list = Cup.objects.all().order_by("c_flow", "-c_edition")
        context["page_title"] = _("Arcade Cups")
        context["page_siblings"] = page_siblings
        context["cups"] = cup_list
        context["menu_type"] = "ARCADES"
        context["categories"] = categories
        return context

class CupIndexCategory(TemplateView):
    template_name = "arcades/index_category.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get("category_slug")
        cup_list = Cup.objects.filter(category__slug=category_slug).order_by("c_flow", "-c_edition")
        context["page_title"] = _("Arcade Cups")
        context["cups"] = cup_list
        context["page_siblings"] = ARCADES_SUB_MENU
        context["menu_type"] = "ARCADES"
        return context

class CupMedals(TemplateView):
    template_name = "arcades/medals.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Medals.objects.all().order_by(
            "-position_1", "-position_2", "-position_3", "-position_4"
        )
        context["page_siblings"] = ARCADES_SUB_MENU
        context["menu_type"] = "EURO"
        context["page_title"] = _("Medals")
        context["teams"] = teams
        return context


class CupRank(TemplateView):
    template_name = "arcades/rank.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = RankAllTime.objects.filter(c_flow=1).order_by(
            "-points", "-gdif", "-gscored"
        )
        context["page_siblings"] = ARCADES_SUB_MENU
        context["menu_type"] = "EURO"
        context["page_title"] = _("Rank")
        context["teams"] = teams
        return context


class CupDetails(MultiTableMixin, TemplateView):
    template_name = "arcades/cup-details.html"  # Create this template
    context_object_name = "objects"
    tables = []
    table_pagination = False


    def dispatch(self, request, *args, **kwargs):
        cup_id = kwargs.get("cup_id")
        cache_key = f'cup_tables_{cup_id}'
        
        # Try to get cached tables
        self.tables = cache.get(cache_key)
        
        if not self.tables:
            cup_object = Cup.objects.filter(id=cup_id).first()
            if cup_object:
                distinct_groups = (
                    RankGroups.objects.filter(c_id=cup_object)
                    .values("g_id")
                    .distinct("g_id")
                    .order_by("g_id")
                )

                self.tables = []
                for g_id in distinct_groups:
                    group = (
                        RankGroups.objects.filter(c_id=cup_object, g_id=g_id["g_id"])
                        .order_by("-points", "-gdif", "-gscored")
                    )
                    table = RankGroupsTable(group)
                    table.paginate(page=1, per_page=100)
                    self.tables.append(table)
                
                # Cache the tables
                cache.set(cache_key, self.tables, 3600)  # Cache for 1 hour

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        final = Game.objects.filter(c_id=cup_id, playoff_position="final")
        final_bronze = Game.objects.filter(
            c_id=cup_id, playoff_position="3/4 final"
        ).first()
        semi_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["s1", "s2"]
        ).order_by("playoff_position", "id")

        quarter_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["q1", "q2", "q3", "q4"]
        ).order_by("playoff_position", "id")

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
        ).order_by("playoff_position", "id")
        eight_finals_cl = Game.objects.filter(
            c_id=cup_id,
            playoff_position__in=[
                "e1_cl",
                "e2_cl",
                "e3_cl",
                "e4_cl",
                "e5_cl",
                "e6_cl",
                "e7_cl",
                "e8_cl",
            ],
        ).order_by("playoff_position", "id")
        url = ""
        if cup_object:
            title = cup_object.c_name
            context["page_title"] = title
            url = reverse(
                "arcade_cup_details",
                kwargs={
                    "cup_id": str(cup_object.pk),
                    "category_slug": str(cup_object.category.slug),
                },
            )
        menu = ARCADES_SUB_MENU
        if cup_object:
            if cup_object.c_groups>0:
                columns_1 = 4
                columns_2 = 8
            else:
                columns_1 = 12
                columns_2 = 12

        # Check if the URL already exists in the `menu`
        if not any(item["url"] == url for item in menu):
            menu.append({"title": cup_object.c_name, "url": url})
        eight_finals_cl_teams = RankGroups.objects.filter(c_id=cup_object,g_id=1).order_by("-points","-gdif","-gscored")[:8]
        if cup_object.is_cl:
            playoff_cols = 6
        else:
            playoff_cols = 3

        context["final"] = final
        context["final_bronze"] = final_bronze
        context["semi_finals"] = semi_finals
        context["quarter_finals"] = quarter_finals
        context["eight_finals"] = eight_finals
        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        context["columns_1"] = columns_1
        context["columns_2"] = columns_2
        context["eight_finals_cl"] = eight_finals_cl
        context["eight_finals_cl_teams"] = eight_finals_cl_teams
        context["playoff_fixtures_cl"] = PLAYOFF_FIXTURES_CL
        context["playoff_cols"] = playoff_cols
        return context
    

class CupFixtures(TemplateView):
    template_name = "arcades/cup-fixtures-group.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        group_id = kwargs.get("group_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        max_round = Game.objects.filter(c_id=cup_id, group_id=group_id)\
                .annotate(cup_round_as_int=Cast("cup_round", IntegerField()))\
                .aggregate(Max("cup_round_as_int"))["cup_round_as_int__max"]
        if not max_round:
            max_round = 1
        rounds = range(1, max_round + 1)
        menu = ARCADES_SUB_MENU
        context["cup"] = cup_object
        context["group_id"] = group_id
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        context["rounds"] = rounds
        context["groups"] = range(1, cup_object.c_groups +1)
        return context
    
class CupDrawTemplate(TemplateView):
    template_name = "arcades/cup-draw.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        pots = CupDraw.objects.filter(c_id=cup_object).order_by("g_id")
        draw = CupTeams.objects.filter(c_id=cup_object).order_by("pk")
        menu = ARCADES_SUB_MENU
        group_numbers = list(range(1, cup_object.c_groups + 1))
        pot_numbers = list(range(1, int(cup_object.c_teams / cup_object.c_groups) + 1))
        # pot_iterations = int(cup.c_teams / cup.c_groups)
        draw_json = []
        group_indexes = defaultdict(int)
        for td in draw:
            group_indexes[td.g_id] += 1
            draw_json.append(
                {
                    "from": "pot_{}".format(td.t_id.pk),
                    "to": "group_{}_{}".format(td.g_id, group_indexes[td.g_id]),
                    "sokker_id": td.t_id.pk,
                }
            )
        col_lg_pots = int(12 / int(cup_object.c_teams / cup_object.c_groups))
        col_lg_groups = int(12 / int(cup_object.c_groups))
     
        if col_lg_pots < 3:
            col_lg_pots=3
        if col_lg_groups < 3:
            col_lg_groups=3

        url = ""
        if cup_object:
            title = cup_object.c_name
            context["page_title"] = title
            url = reverse(
                "arcade_cup_details",
                kwargs={
                    "cup_id": str(cup_object.pk),
                    "category_slug": str(cup_object.category.slug),
                },
            )

        menu = ARCADES_SUB_MENU
        # Check if the URL already exists in the `menu`
        if not any(item["url"] == url for item in menu):
            menu.append({"title": cup_object.c_name, "url": url})
        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        

        if cup_object.is_cl:
            context["col_lg_groups"] = 12
            context["col_lg_pots"] = 3
            context["group_numbers"] = range(1, 2)
            context["pot_numbers"] = range(1, 5)
            context["draw"] = draw
            context["pots"] = pots
        else:
            context["col_lg_groups"] = str(col_lg_groups)
            context["col_lg_pots"] = str(col_lg_pots)
            context["group_numbers"] = group_numbers
            context["pot_numbers"] = pot_numbers
            context["draw"] = draw
            context["pots"] = pots
        context["draw_json"] = json.dumps(draw_json)
        return context
    

class CupStatPotsCLTemplate(TemplateView):
    template_name = "arcades/cup-stat-pots-cl.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        pots = CupDraw.objects.filter(c_id=cup_object).order_by("g_id")
        rank_groups = RankGroups.objects.filter(c_id=cup_object,g_id=1).order_by("-points","-gdif","-gscored").all()
        distinct_pots = pots.values_list('g_id', flat=True).distinct().order_by('g_id')

        url = ""
        menu = ARCADES_SUB_MENU
        # Check if the URL already exists in the `menu`
        if not any(item["url"] == url for item in menu):
            url = url.format(cup_object.pk)
            menu.append({"title": cup_object.c_name, "url": url})
        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        context["distinct_pots"] = distinct_pots
        context["rank_groups"] = rank_groups
        return context
    
class ArcadeTeamDetails(TemplateView):
    template_name = "arcades/team-details.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_id = kwargs.get("team_id")
        team = Team.objects.filter(id=team_id).first()
        cup_teams = CupTeams.objects.filter(t_id=team_id).order_by("-c_id").all()
        print(cup_teams)
        page_title = f"{team.name}"
        context["page_title"] = page_title
        context["team"] = team
        context["menu_type"] = "EURO"
        context["country"] = team.country
        context["cup_teams"] = cup_teams
        return context
    
def CommandFormPlayerUpdate(request):
    c_id = request.GET.get("c_id")
    buffer = StringIO()
    if c_id:
        call_command("draw_arcades", c_id=str(c_id), stdout=buffer)
        cup = Cup.objects.filter(id=c_id).first()
        category_slug = None
        if cup:
           category_slug = cup.category.slug# Get the output from the buffer
        command_output = buffer.getvalue()
        print(command_output)
        buffer.close()
        redirect_url = reverse("arcade_cup_draw", kwargs={"cup_id": str(c_id), "category_slug": category_slug})
        return HttpResponseRedirect(redirect_url)
    else:
        # If 'c_id' is not provided, you can handle the error or set a default value
        return HttpResponse("Error: c_id parameter is missing.", status=400)

@cache_page(timeout=60 * 60 * 24)
def cup_round_image(request, cup_id, round_id):
    # Get default font
    font_path = fm.findfont(fm.FontProperties())
    title_font = ImageFont.truetype(font_path, 30)
    sub_title_font = ImageFont.truetype(font_path, 22)
    game_font = ImageFont.truetype(font_path, 16)

    # Get your data
    cup = Cup.objects.get(id=cup_id)
    games = Game.objects.filter(c_id=cup_id, cup_round=round_id)
    date_round = get_cup_round_date(cup.c_start_date, round_id).strftime("%d.%m.%Y")
    # Create image
    y = 95
    height = 20 + (len(games) * 30) + y
    img = Image.new('RGB', (800, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw title

    draw.text((20, 20), f"Cup: {cup.c_name} - Round {round_id} ", fill='black', font=title_font)
    draw.text((20, 50), f"Date {date_round}", fill='black', font=sub_title_font)
    # Draw games
    width = 800
    padding = 20
    flag_size = (26, 17)  # Adjust size as needed

    for game in games:
        # Home team flag
        home_flag = get_flag_image(game.t_id_h.country.code, flag_size)
        if home_flag:
            img.paste(home_flag, (padding, y))

        # Away team flag
        away_flag = get_flag_image(game.t_id_v.country.code, flag_size)
        if away_flag:
            img.paste(away_flag, (width - padding - flag_size[0], y))
   
        text_home = f"{game.t_id_h.name}" 
        text_result = f"{game.goals_home} - {game.goals_away}".replace("None", "")
        text_away = f"{game.t_id_v.name}"

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
        draw.text((60, y), text_home, fill='black', font=game_font)
        draw.text((380, y), text_result, fill='black', font=game_font)
        draw.text((500, y), text_away, fill='black', font=game_font)
        circle_radius = 8
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

    # Get your data
    cup = Cup.objects.get(id=cup_id)
    group = RankGroups.objects.filter(c_id=cup, g_id=group_id).order_by("-points", "-gdif", "-gscored")
    standings = []
    position = 1
    title = f"Group {group_id}"
    for team in group:
        promotion = False
        relegation = False
        if cup.is_cl:
            if position <=8:
                promotion = True
            elif position > 28:
                relegation = True
            print(position,promotion,relegation)
       
        else:
            if position <=   cup.c_g_winners / cup.c_groups:
                promotion = True
        standings.append({
            "position": position,
            "name": team.t_id.name,
            "games": team.games,
            "wins": team.wins,
            "draw": team.draw,
            "lost": team.loose,
            "gd": str(team.gscored)  + " - " + str(team.grecieved),
            "pts": team.points,
            "promotion": promotion,
            "relegation": relegation,
            "country": team.t_id.country.code
        })
        position += 1
    return create_standings_table_image(standings, title, title_font)


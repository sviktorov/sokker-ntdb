from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, RankGroups, Game, Medals, RankAllTime, CupCategory, CupDraw, CupTeams
from .tables import RankGroupsTable
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect
from .utils import generate_fixtures_cl
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast
import json
from collections import defaultdict


ARCADES_SUB_MENU = [
    {"title": _("Arcade tournaments"), "url": "/en/arcades"},
]


def pass_category_to_menu(category: CupCategory):
    menu = []
    for item in ARCADES_SUB_MENU:
        item["url"] = item["url"].format(category.slug)
        menu.append(item)
    return menu


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

    def dispatch(self, request, *args, **kwargs):
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()

        if cup_object and self.tables == []:
            distinct_groups = (
                RankGroups.objects.filter(c_id=cup_object)
                .values("g_id")
                .distinct("g_id")
                .order_by("g_id")
            )

            for g_id in distinct_groups:
                group = (
                    RankGroups.objects.filter(c_id=cup_object, g_id=g_id["g_id"])
                    .order_by("-points", "-gdif", "-gscored")
                )
                self.tables.append(
                    RankGroupsTable(group),
                )
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
            url = reverse(
                "arcade_cup_details",
                kwargs={
                    "cup_id": str(cup_object.pk),
                    "category_slug": str(cup_object.category.slug),
                },
            )
        menu = ARCADES_SUB_MENU
        if cup_object:
            if cup_object.c_groups>1:
                columns_1 = 4
                columns_2 = 8
            else:
                columns_1 = 12
                columns_2 = 12

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
        context["menu_type"] = "EURO"
        context["columns_1"] = columns_1
        context["columns_2"] = columns_2
        
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
        context["pots"] = pots
        context["group_numbers"] = group_numbers
        context["pot_numbers"] = pot_numbers
        context["col_lg_groups"] = str(col_lg_groups)
        context["col_lg_pots"] = str(col_lg_pots)
        context["draw"] = draw
        context["draw_json"] = json.dumps(draw_json)
        return context

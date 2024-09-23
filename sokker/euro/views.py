from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, RankGroups, Game, Medals, RankAllTime
from .tables import RankGroupsTable
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

EURO_SUB_MENU = [
    {"title": _("Euros - listing"), "url": "/en/euro"},
    {"title": _("Medals"), "url": "/en/euro/medals"},
    {"title": _("Rank"), "url": "/en/euro/rank"},
]


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


class CupDetails(MultiTableMixin, TemplateView):
    template_name = "euro/cup-details.html"  # Create this template
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
                    .order_by("-points")
                    .order_by("-gdif")
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
            url = reverse("cup_details", kwargs={"cup_id": str(cup_object.pk)})
        menu = EURO_SUB_MENU

        # Check if the URL already exists in the `menu`
        if not any(item["url"] == url for item in menu):
            menu.append({"title": cup_object.c_name, "url": url})
        context["page_siblings"] = []
        context["final"] = final
        context["final_bronze"] = final_bronze
        context["semi_finals"] = semi_finals
        context["quarter_finals"] = quarter_finals
        context["eight_finals"] = eight_finals

        context["cup"] = cup_object
        context["page_siblings"] = menu
        context["menu_type"] = "EURO"
        return context

from .models import Player, ArchivePlayer
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .utils import get_gk_wrapper, get_def_wrapper, get_mid_wrapper, get_att_wrapper
from sokker_base.models import Country, UserCountry
from admin_numeric_filter.admin import RangeNumericFilter
from .forms import PlayerAdminForm
from sokker_base.api import get_sokker_player_data
from .pharsers import parser_player
from django.urls import reverse
from django.utils.html import format_html


class SkillRangeNumericFilter(RangeNumericFilter):
    MAX_DECIMALS = 18
    STEP = 1


class CountryFilter(admin.SimpleListFilter):
    title = _("Country")
    parameter_name = "countryid"
    template = "django_admin_listfilter_dropdown/dropdown_filter.html"

    def lookups(self, request, model_admin):
        user = request.user
        user_countries = UserCountry.objects.values("country").filter(user=user)
        if not user.is_superuser:
            filter_tuple = list(
                (country.code, country.name)
                for country in Country.objects.filter(active=True).filter(
                    pk__in=user_countries
                )
            )
        else:
            filter_tuple = list(
                (country.code, country.name)
                for country in Country.objects.filter(active=True)
            )
        return filter_tuple

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(countryid=self.value())


# from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter
class AgeEqualFilter(admin.SimpleListFilter):
    title = _("Age Equal")
    parameter_name = "age"
    template = "django_admin_listfilter_dropdown/dropdown_filter.html"

    def lookups(self, request, model_admin):
        filter_tuple = [(f"{i}", f"{i}") for i in range(16, 40)]
        return filter_tuple

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(age=self.value())


class AgeLessFilter(admin.SimpleListFilter):
    title = _("Age Less")
    parameter_name = "age_less"
    template = "django_admin_listfilter_dropdown/dropdown_filter.html"

    def lookups(self, request, model_admin):
        filter_tuple = [(f"{i}", f"<={i}") for i in range(16, 40)]
        return filter_tuple

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(age__lte=self.value())


class PlayerAdmin(ImportExportModelAdmin):
    country = None
    form = PlayerAdminForm
    list_per_page = 50
    list_display = [
        "full_name",
        "injurydays",
        "age",
        "value",
        "position_with_class",
        "skillform",
        "skillstamina",
        "skillkeepr_with_class",
        "skillpace_with_class",
        "skillscoring_with_class",
        "skilltechnique_with_class",
        "skillpassing_with_class",
        "skillplaymaking_with_class",
        "skilldefending_with_class",
        "skillexperience",
        "skillteamwork",
        "skilldiscipline",
        "get_defender_points",
        "get_midfielder_points",
        "get_attacker_points",
        "get_goalie_points",
        "position_score",
        "date",
        "edit_button",
        "daily_update",
    ]  # Add any other fields you want to display in the list
    readonly_fields = (
        "injurydays",
        "teamid",
        "youthteamid",
        "value",
        "wage",
        "age",
        "cards",
        "goals",
        "assists",
        "matches",
        "ntmatches",
        "ntcards",
        "ntgoals",
        "ntassists",
        "national",
        "skillform",
        "skillteamwork",
        "skillexperience",
        "skillexperience",
        "skilldiscipline",
        "transferlist",
        "date",
        "height",
        "weight",
        "modified",
        "daily_update",
    )
    ordering = ("-value",)
    list_filter = [
        CountryFilter,
        "position",
        "national",
        AgeEqualFilter,
        AgeLessFilter,
        ("skillkeeper", SkillRangeNumericFilter),
        ("skillpace", SkillRangeNumericFilter),
        ("skillscoring", SkillRangeNumericFilter),
        ("skilltechnique", SkillRangeNumericFilter),
        ("skillpassing", SkillRangeNumericFilter),
        ("skillplaymaking", SkillRangeNumericFilter),
        ("skilldefending", SkillRangeNumericFilter),
        "teamid",
    ]  # Add 'countryid' to filter optionsßß
    search_fields = ["sokker_id", "name", "surname"]

    def save_model(self, request, obj, form, change):
        response = get_sokker_player_data(obj.sokker_id)
        obj = parser_player(response, obj)
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        user = request.user

        country_code = request.GET.get("countryid")
        if not country_code:
            user_country = (
                UserCountry.objects.values("country__code")
                .filter(user=user)
                .filter(is_default=True)
                .first()
            )
            if user_country:
                country_code = user_country.get("country__code")
        self.country = Country.objects.filter(code=country_code).first()
        extra_context["country"] = self.country
        extra_context["extra_title"] = _("Players")
        extra_context["extra_actions"] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            gk_points=get_gk_wrapper(),
        )
        queryset = queryset.annotate(
            def_points=get_def_wrapper(),
        )

        queryset = queryset.annotate(
            mid_points=get_mid_wrapper(),
        )

        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
        )
        user = request.user
        country_id = request.GET.get("countryid")
        if not country_id:
            user_country = (
                UserCountry.objects.values("country__code")
                .filter(user=user)
                .filter(is_default=True)
                .first()
            )
            if user_country:
                country_code = user_country.get("country__code")
                queryset = queryset.filter(countryid=country_code)
        return queryset

    def edit_button(self, obj):
        url = reverse(
            "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
            args=[obj.pk],
        )
        return format_html('<a href="{}?countryid={}">Edit</a>', url, obj.countryid)

    edit_button.short_description = _("Edit")

    def full_name(self, obj):
        full_name = ""
        if obj.name and obj.surname:
            full_name = obj.name + " " + obj.surname  # Change the label as required
        else:
            full_name = obj.sokker_id
        return format_html(
            '<a href="https://sokker.org/player/PID/{}" target="_blank">{}</a>',
            obj.sokker_id,
            full_name,
        )

    full_name.short_description = _("Name")  # Set the custom label

    def get_goalie_points(self, obj):
        return obj.gk_points

    get_goalie_points.short_description = "GK"  # Set the column header
    get_goalie_points.admin_order_field = "gk_points"  # Set the sorting field

    def get_defender_points(self, obj):
        return obj.def_points

    get_defender_points.short_description = "DEF"  # Set the column header
    get_defender_points.admin_order_field = "def_points"  # Set the sorting field

    def get_midfielder_points(self, obj):
        return obj.mid_points

    get_midfielder_points.short_description = "MID"  # Set the column header
    get_midfielder_points.admin_order_field = "mid_points"  # Set the sorting field

    def get_attacker_points(self, obj):
        return obj.att_points

    get_attacker_points.short_description = "ATT"  # Set the column header
    get_attacker_points.admin_order_field = "att_points"  # Set the sorting field

    def skillpace_with_class(self, obj):
        return format_html(
            '<span class="skill-pace {}">{}</span>', obj.position, obj.skillpace
        )

    skillpace_with_class.short_description = _("Pace")
    skillpace_with_class.admin_order_field = "skillpace"

    def skillkeepr_with_class(self, obj):
        return format_html(
            '<span class="skill-keeper {}">{}</span>', obj.position, obj.skillkeeper
        )

    skillkeepr_with_class.short_description = _("Gk")
    skillkeepr_with_class.admin_order_field = "skillkeeper"

    def skillpassing_with_class(self, obj):
        return format_html(
            '<span class="skill-pass {}">{}</span>', obj.position, obj.skillpassing
        )

    skillpassing_with_class.short_description = _("Pass")
    skillpassing_with_class.admin_order_field = "skillpassing"

    def skillplaymaking_with_class(self, obj):
        return format_html(
            '<span class="skill-playmaking {}">{}</span>',
            obj.position,
            obj.skillplaymaking,
        )

    skillplaymaking_with_class.short_description = _("Plm.")
    skillplaymaking_with_class.admin_order_field = "skillplaymaking"

    def skilldefending_with_class(self, obj):
        return format_html(
            '<span class="skill-defending {}">{}</span>',
            obj.position,
            obj.skilldefending,
        )

    skilldefending_with_class.short_description = _("Def.")
    skilldefending_with_class.admin_order_field = "skilldefending"

    def skillscoring_with_class(self, obj):
        return format_html(
            '<span class="skill-scoring {}">{}</span>',
            obj.position,
            obj.skillscoring,
        )

    skillscoring_with_class.short_description = _("Att.")
    skillscoring_with_class.admin_order_field = "skillscoring"

    def skilltechnique_with_class(self, obj):
        return format_html(
            '<span class="skill-technique {}">{}</span>',
            obj.position,
            obj.skilltechnique,
        )

    skilltechnique_with_class.short_description = _("Tech.")
    skilltechnique_with_class.admin_order_field = "skilltechnique"

    def position_with_class(self, obj):
        return format_html(
            '<span class="skill-position {}">{}</span>',
            obj.position,
            obj.position,
        )

    position_with_class.short_description = _("pos.")
    position_with_class.admin_order_field = "position"


admin.site.register(Player, PlayerAdmin)


class ArchivePlayerAdmin(ImportExportModelAdmin):
    list_display = [
        "full_name",
        "age",
        "value",
        "position",
        "skillstamina",
        "skillpace",
        "skillkeeper",
        "skilldefending",
        "skillscoring",
        "skilltechnique",
        "skillpassing",
        "skillplaymaking",
        "get_defender_points",
        "get_midfielder_points",
        "get_attacker_points",
        "get_goalie_points",
        "daily_update",
    ]  # Add any other fields you want to display in the list
    ordering = ("-value",)
    list_filter = [
        CountryFilter,
        "position",
        "national",
        AgeEqualFilter,
        AgeLessFilter,
    ]  # Add 'countryid' to filter optionsßß
    search_fields = ["sokker_id", "name", "surname"]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        user = request.user

        country_code = request.GET.get("countryid")
        if not country_code:
            user_country = (
                UserCountry.objects.values("country__code")
                .filter(user=user)
                .filter(is_default=True)
                .first()
            )
            if user_country:
                country_code = user_country.get("country__code")
        self.country = Country.objects.filter(code=country_code).first()
        extra_context["country"] = self.country
        extra_context["extra_title"] = _("Archived Players")
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            gk_points=get_gk_wrapper(),
        )
        queryset = queryset.annotate(
            def_points=get_def_wrapper(),
        )

        queryset = queryset.annotate(
            mid_points=get_mid_wrapper(),
        )

        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
        )
        user = request.user

        country_id = request.GET.get("countryid")
        if not country_id:
            user_country = (
                UserCountry.objects.values("country__code")
                .filter(user=user)
                .filter(is_default=True)
                .first()
            )
            if user_country:
                country_code = user_country.get("country__code")
                queryset = queryset.filter(countryid=country_code)
        return queryset

    def full_name(self, obj):
        if obj:
            return (obj.name or "") + " " + (obj.surname or "")
        return ""

    full_name.short_description = _("Name")  # Set the custom label

    def get_goalie_points(self, obj):
        return obj.gk_points

    get_goalie_points.short_description = "GK"  # Set the column header
    get_goalie_points.admin_order_field = "gk_points"  # Set the sorting field

    def get_defender_points(self, obj):
        return obj.def_points

    get_defender_points.short_description = "DEF"  # Set the column header
    get_defender_points.admin_order_field = "def_points"  # Set the sorting field

    def get_midfielder_points(self, obj):
        return obj.mid_points

    get_midfielder_points.short_description = "MID"  # Set the column header
    get_midfielder_points.admin_order_field = "mid_points"  # Set the sorting field

    def get_attacker_points(self, obj):
        return obj.att_points

    get_attacker_points.short_description = "ATT"  # Set the column header
    get_attacker_points.admin_order_field = "att_points"  # Set the sorting field


admin.site.register(ArchivePlayer, ArchivePlayerAdmin)

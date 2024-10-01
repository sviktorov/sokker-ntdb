from .models import Player, ArchivePlayer
from django_tables2.views import MultiTableMixin
from django.utils.translation import gettext_lazy as _
from .utils import (
    get_fullname_wrapper,
    get_att_wrapper,
    get_gk_wrapper,
    get_def_wrapper,
    get_mid_wrapper,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from .menu import NTDB_SUB_MENU
from .filters import PlayerAgeFilter, ArchivePlayerAgeFilter
from .tables import (
    GKPlayerTable,
    DefPlayerTable,
    MidPlayerTable,
    AttPlayerTable,
    return_distinct_all_time_records_by_position,
    GKArchivePlayerTable,
    DefArchivePlayerTable,
    MidArchivePlayerTable,
    AttArchivePlayerTable,
    ArchivePlayerDetailsTable,
)
from sokker_base.models import Country, PointsRequirementsCountry, Team
from django.db.models.functions import Lower
from django.core.management import call_command
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import StringIO
from django_filters.views import FilterView
import logging
import urllib.parse
from decimal import Decimal
from datetime import datetime
from django.urls import reverse
from django.http import HttpResponse
import os

logger = logging.getLogger(__name__)


class NTDBIndex(TemplateView):
    template_name = "ntdb/ntdb-index.html"  # Create this template


class PlayerUpdate(TemplateView):
    template_name = "ntdb/skill-form.html"  # Create this template

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        try:
            parsed_body = urllib.parse.parse_qs(request.body.decode("utf-8"))
        except UnicodeDecodeError:
            # Fall back to a different encoding if UTF-8 fails
            parsed_body = urllib.parse.parse_qs(request.body.decode("latin-1"))

        logger.debug("Body: %s", parsed_body)

        # Process the form data here
        pid = parsed_body.get("pid", [""])[0]
        age = parsed_body.get("age", [""])[0]
        countryid = parsed_body.get("countryid", [""])[0]
        sta = parsed_body.get("sta", [""])[0]
        kee = parsed_body.get("kee", [""])[0]
        pac = parsed_body.get("pac", [""])[0]
        def_skill = parsed_body.get("def", [""])[0]
        tec = parsed_body.get("tec", [""])[0]
        str_skill = parsed_body.get("str", [""])[0]
        pas = parsed_body.get("pas", [""])[0]
        pla = parsed_body.get("pla", [""])[0]

        if not pid:
            context = self.get_context_data(**kwargs)  # Optionally, get context data
            return self.render_to_response(context)

        player = Player.objects.filter(sokker_id=pid).first()

        req = PointsRequirementsCountry.objects.filter(
            country__code=countryid, age=age
        ).first()
        # fallback to bulgaria
        if not req:
            req = PointsRequirementsCountry.objects.filter(
                country__code=54, age=age
            ).first()

        if not player:
            player = Player()
        if pid:
            player.sokker_id = pid
            player.countryid = countryid
            player.age = age
            player.skillstamina = sta
            player.skillkeeper = kee
            player.skillpace = pac
            player.skilldefending = def_skill
            player.skilltechnique = tec
            player.skillscoring = str_skill
            player.skillpassing = pas
            player.skillplaymaking = pla
            if player.position == "" or not player.position:
                player.position = player.best_position()
            # Get the current date and time
            current_date = datetime.now()
            # Format the current date as a string
            date_string = current_date.strftime("%Y-%m-%d %H:%M:%S")
            player.date = date_string

            if req is not None and (
                Decimal(player.calculate_att_points()) >= req.att_points
                or Decimal(player.calculate_def_points()) >= req.def_points
                or Decimal(player.calculate_mid_points()) >= req.mid_points
                or Decimal(player.calculate_gk_points()) >= req.gk_points
            ):
                player.save()
                logger.debug("Saved: %s", player)

                url = f"https://sokker.org/api/player/{player.sokker_id}"
                print("sokker id" ": " + str(player.sokker_id))
                # Send GET request
                headers = {"accept": "application/json"}
                response = requests.get(url, headers=headers)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Print the JSON response
                    data = response.json()
                    info = data["info"]
                    team = info["team"]
                    country = info["country"]
                    value = info["value"]
                    wage = info["wage"]
                    characteristics = info["characteristics"]
                    skills = info["skills"]
                    stats = info["stats"]
                    nationalStats = info["nationalStats"]
                    youthTeamId = info["youthTeamId"]
                    injury = info["injury"]

                    player.name = info["name"]["name"]
                    player.surname = info["name"]["surname"]
                    team_object = Team.objects.filter(id=team["id"]).first()
                    if team_object:
                        player.teamid = team_object
                    else:
                        player.teamid = None
                    player.countryid = country["code"]

                    # its in zl
                    player.wage = wage["value"] / 2
                    player.value = value["value"] / 2
                    player.age = characteristics["age"]
                    player.height = characteristics["height"]
                    player.skillform = skills["form"]
                    player.skilldiscipline = skills["tacticalDiscipline"]
                    player.skillteamwork = skills["teamwork"]
                    player.skillexperience = skills["experience"]
                    player.cards = stats["cards"]["cards"]
                    player.goals = stats["goals"]
                    player.assists = stats["assists"]
                    player.matches = stats["matches"]

                    player.ntcards = nationalStats["cards"]["cards"]
                    player.ntgoals = nationalStats["goals"]
                    player.ntassists = nationalStats["assists"]
                    player.ntassists = nationalStats["matches"]
                    team_object_youth = Team.objects.filter(id=youthTeamId).first()
                    if team_object_youth:
                        player.youthteamid = team_object_youth
                    else:
                        player.youthteamid = None
                    player.injurydays = injury["daysRemaining"]
                    player.daily_update = current_date
                    player.save()

        context = self.get_context_data(**kwargs)  # Optionally, get context data
        return self.render_to_response(context)


@login_required
def CommandUpdateTeams(request):
    buffer = StringIO()
    call_command("sokker_update_teams_names")
    # Get the output from the string buffer
    command_output = buffer.getvalue()

    # Close the string buffer
    buffer.close()
    return HttpResponse(command_output)


@login_required
def CommandFixPlayerPosition(request):
    buffer = StringIO()
    call_command("fix_player_position")
    # Get the output from the string buffer
    command_output = buffer.getvalue()
    # Close the string buffer
    buffer.close()
    return HttpResponse(command_output)


@login_required
def CommandFormPlayerUpdate(request):
    buffer = StringIO()
    call_command("sokker_update_public")
    # Get the output from the string buffer
    command_output = buffer.getvalue()

    # Close the string buffer
    buffer.close()
    return HttpResponse(command_output)


@login_required
def CommandArchivePlayers(request):
    buffer = StringIO()
    call_command("copy_players_to_archive")
    # Get the output from the string buffer
    command_output = buffer.getvalue()

    # Close the string buffer
    buffer.close()
    return HttpResponse(command_output)


class PlayerHistory(MultiTableMixin, TemplateView):
    template_name = "ntdb/player-history.html"  # Create this template
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    player = None
    tables = []

    def dispatch(self, request, *args, **kwargs):

        self.country_name = kwargs.get("country_name")
        self.sokker_id = kwargs.get("sokker_id")

        self.country = (
            Country.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower=self.country_name.lower())
            .first()
        )

        try:
            sokker_id = int(self.sokker_id)
            player = Player.objects.filter(sokker_id=sokker_id).first()
        except ValueError:
            # Handle the error, log it, or provide a fallback
            player = None  # or some other default behavior
        if not player:
            player = ArchivePlayer.objects.filter(sokker_id=self.sokker_id).first()

        self.player = player
        if self.player:
            self.tables = [
                ArchivePlayerDetailsTable(
                    ArchivePlayer.objects.annotate(
                        fullname=get_fullname_wrapper(),
                        att_points=get_att_wrapper(),
                        def_points=get_def_wrapper(),
                        mid_points=get_mid_wrapper(),
                        gk_points=get_gk_wrapper(),
                    ).filter(sokker_id=self.player.sokker_id),
                    order_by="-age",
                ),
            ]

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional variables to the context
        menu = NTDB_SUB_MENU
        title = _("Player History")
        if self.player:
            title = self.player.name + " " + self.player.surname + " - " + _("History")
        item = {"title": title, "url": ""}
        if len(menu) < 3:
            menu.append(item)

        context["page_title"] = title
        context["page_siblings"] = menu
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        context["player"] = self.player
        return context


class BestPlayers(MultiTableMixin, FilterView):
    template_name = "ntdb/players-best.html"
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    tables = []
    age_filter = None
    filterset_class = PlayerAgeFilter
    table_pagination = {"per_page": 50}

    def dispatch(self, request, *args, **kwargs):
        self.country_name = kwargs.get("country_name")
        self.country = (
            Country.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower=self.country_name.lower())
            .first()
        )
        self.age_filter = request.GET.get("age")
        if not self.age_filter:
            start_age = 16
            end_age = 40
        else:
            start_age = self.age_filter
            end_age = self.age_filter

        if self.country:
            self.tables = [
                GKPlayerTable(
                    Player.objects.annotate(fullname=get_fullname_wrapper())
                    .filter(position="GK")
                    .filter(countryid=self.country.code)
                    .filter(age__lte=end_age)
                    .filter(age__gte=start_age)
                    .exclude(name="")
                    .exclude(surname=""),
                    order_by="-gk_points",
                ),
                DefPlayerTable(
                    Player.objects.annotate(fullname=get_fullname_wrapper())
                    .filter(position="DEF")
                    .filter(countryid=self.country.code)
                    .filter(age__lte=end_age)
                    .filter(age__gte=start_age)
                    .exclude(name="")
                    .exclude(surname=""),
                    order_by="-def_points",
                ),
                MidPlayerTable(
                    Player.objects.annotate(fullname=get_fullname_wrapper())
                    .filter(position="MID")
                    .filter(countryid=self.country.code)
                    .filter(age__lte=end_age)
                    .filter(age__gte=start_age)
                    .exclude(name="")
                    .exclude(surname=""),
                    order_by="-mid_points",
                ),
                AttPlayerTable(
                    Player.objects.annotate(fullname=get_fullname_wrapper())
                    .filter(position="ATT")
                    .filter(countryid=self.country.code)
                    .filter(age__lte=end_age)
                    .filter(age__gte=start_age)
                    .exclude(name="")
                    .exclude(surname=""),
                    order_by="-att_points",
                ),
            ]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional variables to the context
        context["page_title"] = _("Best Players")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        return context


def debug_view(request, country_name):
    # Get the client's IP address
    # Set the log file path (adjust this as needed)
    LOG_FILE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ip_logs.txt"
    )
    ip_address = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT")

    # Get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the IP address and current time to a file
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(
            f"IP: {ip_address}, DateTime: {current_time} , UserAgent: {user_agent} \n"
        )

    # Your view logic here
    return HttpResponse("Best players view was moved")


class BestPlayersAll(MultiTableMixin, FilterView):
    template_name = "ntdb/players-best.html"
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    age_filter = None
    filterset_class = ArchivePlayerAgeFilter
    table_pagination = {"per_page": 100}

    def dispatch(self, request, *args, **kwargs):

        self.country_name = kwargs.get("country_name")
        self.country = (
            Country.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower=self.country_name.lower())
            .first()
        )

        self.age_filter = request.GET.get("age")
        if not self.age_filter:
            start_age = 16
            end_age = 40
        else:
            start_age = self.age_filter
            end_age = self.age_filter

        self.tables = [
            GKArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "GK", self.country, start_age, end_age
                ),
                order_by="-gk_points",
            ),
            DefArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "DEF", self.country, start_age, end_age
                ),
                order_by="-def_points",
            ),
            MidArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "MID", self.country, start_age, end_age
                ),
                order_by="-mid_points",
            ),
            AttArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "ATT", self.country, start_age, end_age
                ),
                order_by="-att_points",
            ),
        ]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional variables to the context
        context["page_title"] = _("Best Players All Time")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        return context

from .models import Player, ArchivePlayer
from django_tables2.views import MultiTableMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import (
    get_fullname_wrapper,
    get_att_wrapper,
    get_gk_wrapper,
    get_def_wrapper,
    get_mid_wrapper,
    get_wing_wrapper,
)
from .forms import PlayerManualUpdateForm, PlayerForm
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView
from .menu import NTDB_SUB_MENU
from .filters import PlayerAgeFilter, ArchivePlayerAgeFilter
from .tables import (
    GKPlayerTable,
    DefPlayerTable,
    MidPlayerTable,
    WingPlayerTable,
    AttPlayerTable,
    return_distinct_all_time_records_by_position,
    GKArchivePlayerTable,
    DefArchivePlayerTable,
    MidArchivePlayerTable,
    WingArchivePlayerTable,
    AttArchivePlayerTable,
    ArchivePlayerDetailsTable,
    NTGamesArchivePlayerTable,
    NTGoalsArchivePlayerTable,
    NTAssistsArchivePlayerTable,
    GamesArchivePlayerTable,
    GoalsArchivePlayerTable,
    AssistsArchivePlayerTable,
    NTTeamsStatsTable,
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
from .utils import extract_skill_value, set_pharse_player_data
from .models import NTTeamsStats
import json

logger = logging.getLogger(__name__)


class NTDBIndex(TemplateView):
    template_name = "ntdb/ntdb-index.html"

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            parsed_body = urllib.parse.parse_qs(request.body.decode("utf-8"))
        except UnicodeDecodeError:
            parsed_body = urllib.parse.parse_qs(request.body.decode("latin-1"))

        pid = parsed_body.get("pid", [""])[0]
        player_data = parsed_body.get("player_data", [""])[0]   

        logger.debug("Body: %s", parsed_body)
        
        # Process form data here
        # Add your form processing logic
        
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("NTDB Index")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        return context


class PlayerManualUpdate(LoginRequiredMixin, FormView):
    template_name = "ntdb/player-manual-update.html"
    form_class = PlayerManualUpdateForm

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class()
        step = request.POST.get("step", None)
        playerForm = None
        saved = False
        sokker_id = request.GET.get("sokker_id", None)
        if step == "1":
            form = self.form_class(request.POST)
            if form.is_valid():
                pid = form.cleaned_data["pid"]
                player_data = form.cleaned_data["player_data"]
                # Extract values for each skill
                sta = extract_skill_value(player_data, "stamina")
                kee = extract_skill_value(player_data, "keeper")
                pac = extract_skill_value(player_data, "pace")
                def_skill = extract_skill_value(player_data, "defender")
                tec = extract_skill_value(player_data, "technique")
                pla = extract_skill_value(player_data, "playmaker")
                pas = extract_skill_value(player_data, "passing")
                str_skill = extract_skill_value(player_data, "striker")

                player = Player.objects.filter(sokker_id=pid).first()

                # Initialize form data with skills from parameters
                player_form_data = {
                    'sokker_id': pid,
                    'skillstamina': sta,
                    'skillkeeper': kee,
                    'skillpace': pac,
                    'skilldefending': def_skill,
                    'skilltechnique': tec,
                    'skillplaymaking': pla,
                    'skillpassing': pas,
                    'skillscoring': str_skill,
                    'player_data': player_data,
                }

                # If player exists, add additional fields from database
                if player:
                    playerForm = PlayerForm(instance=player, initial=player_form_data)
                else:
                    playerForm = PlayerForm(initial=player_form_data)
            else:
                playerForm = None

        if step == "2":
            playerForm = PlayerForm(request.POST)
            if playerForm.is_valid():  # Check if form is valid first
                # Create data dictionary for form initialization
                form_data = {
                    'pid': playerForm.cleaned_data["sokker_id"],
                    'player_data': playerForm.cleaned_data["player_data"]
                }
                form = PlayerManualUpdateForm(initial=form_data)
                # Set the date before saving
                player = Player.objects.filter(sokker_id=playerForm.cleaned_data["sokker_id"]).first()
                if player:
                    player.skillstamina = playerForm.cleaned_data["skillstamina"]
                    player.skillkeeper = playerForm.cleaned_data["skillkeeper"]
                    player.skillpace = playerForm.cleaned_data["skillpace"]
                    player.skilldefending = playerForm.cleaned_data["skilldefending"]
                    player.skilltechnique = playerForm.cleaned_data["skilltechnique"]
                    player.skillplaymaking = playerForm.cleaned_data["skillplaymaking"]
                    player.skillpassing = playerForm.cleaned_data["skillpassing"]
                    player.skillscoring = playerForm.cleaned_data["skillscoring"]
                    player.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    saved = True
                    player.save()
                else:
                    player = Player()
                    player.sokker_id = playerForm.cleaned_data["sokker_id"]
                    player.skillstamina = playerForm.cleaned_data["skillstamina"]
                    player.skillkeeper = playerForm.cleaned_data["skillkeeper"]
                    player.skillpace = playerForm.cleaned_data["skillpace"]
                    player.skilldefending = playerForm.cleaned_data["skilldefending"]
                    player.skilltechnique = playerForm.cleaned_data["skilltechnique"]
                    player.skillplaymaking = playerForm.cleaned_data["skillplaymaking"]
                    player.skillpassing = playerForm.cleaned_data["skillpassing"]
                    player.skillscoring = playerForm.cleaned_data["skillscoring"]
                    player.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    player.save()
                    saved = True
                  
                
            else:
                # Handle invalid form case
               
                form = PlayerManualUpdateForm(initial={'pid': sokker_id})  # Create empty form if validation fails
      
        context = self.get_context_data(form=form, playerForm=playerForm, saved=saved, **kwargs)
        return self.render_to_response(context)
        
    def get(self, request, *args, **kwargs):
        # Get sokker_id from URL parameters
        sokker_id = request.GET.get("sokker_id", None)
        # Initialize form with sokker_id if provided
        player_data = set_pharse_player_data(None)
        if sokker_id:
            player = Player.objects.filter(sokker_id=sokker_id).first()
            if player:
                player_data = set_pharse_player_data(player) 

        form = self.form_class(initial={'pid': sokker_id, 'player_data': player_data}) if sokker_id else self.form_class(initial={'player_data': player_data})
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Player Manual Update")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        return context

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
            logger.error("No requirements found for country: %s age: %s", countryid, age)
            req = PointsRequirementsCountry.objects.filter(
                country__code=countryid, age=28
            ).first()
        if not req:
            logger.error("No requirements found for country: %s age: %s", "BG", age)
            req = PointsRequirementsCountry.objects.filter(
                country__code=54, age=28
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
                logger.debug("Player saved: %s", player)


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
                    logger.debug("Player saved: %s", player)
                else:
                    logger.error("call to sokker failed: %s", pid)
            else:
                logger.error("Player do not meet requirements: %s", pid)
        else:
            logger.error("Player not found: %s", pid)

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
    is_active = False
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
            self.is_active = True
        except ValueError:
            # Handle the error, log it, or provide a fallback
            player = None  # or some other default behavior
        if not player:
            player = ArchivePlayer.objects.filter(sokker_id=self.sokker_id).order_by("-age").first()
            self.is_active = False
        self.player = player
        if self.player:
            self.tables = [
                ArchivePlayerDetailsTable(
                    ArchivePlayer.objects.annotate(
                        fullname=get_fullname_wrapper(),
                        att_points=get_att_wrapper(),
                        def_points=get_def_wrapper(),
                        mid_points=get_mid_wrapper(),
                        wing_points=get_wing_wrapper(),
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
        context["is_active"] = self.is_active
        return context


class BestPlayers(MultiTableMixin, FilterView):
    template_name = "ntdb/players-best.html"
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    tables = []
    age_filter = None
    filterset_class = PlayerAgeFilter
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
                WingPlayerTable(
                    Player.objects.annotate(fullname=get_fullname_wrapper())
                    #.filter(position="MID")
                    .filter(countryid=self.country.code)
                    .filter(age__lte=end_age)
                    .filter(age__gte=start_age)
                    .exclude(name="")
                    .exclude(surname=""),
                    order_by="-wing_points",
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
        context["submenu"] = 'best' 
        context["active_table"] = 1
        return context


class BestPlayersAllStats(MultiTableMixin, FilterView):
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
            NTGamesArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "NT_GAMES", self.country, start_age, end_age
                ),
                order_by="ntmatches_max",
            ),
            NTGoalsArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "NT_GOALS", self.country, start_age, end_age
                ),
                order_by="ntgoals_max",
            ),
            NTAssistsArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "NT_ASSISTS", self.country, start_age, end_age
                ),
                order_by="ntassists_max",
            ),
            GamesArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "GAMES", self.country, start_age, end_age
                ),
                order_by="games_max",
            ),
            GoalsArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "GOALS", self.country, start_age, end_age
                ),
                order_by="goals_max",
            ),
            AssistsArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "ASSISTS", self.country, start_age, end_age
                ),
                order_by="assists_max",
            ),
           
        ]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional variables to the context
        context["page_title"] = _("Best Players All Time Stats")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        context["submenu"] = 'all_stats'
        context["active_table"] = 1
        return context


class BestPlayersAllStatsTeams(MultiTableMixin, TemplateView):
    template_name = "ntdb/players-best.html"
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    age_filter = None
    table_pagination = {"per_page": 100}
    active_table = 1
    def dispatch(self, request, *args, **kwargs):
        self.country_name = kwargs.get("country_name")
        self.country = (
            Country.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower=self.country_name.lower())
            .first()
        )

        # Get sort parameters from request
        table1_sort = request.GET.get('table_0-sort', None)
        table2_sort = request.GET.get('table_1-sort', None)
        
        # Set active_table based on sort parameters
        if table1_sort and table2_sort:
            self.active_table = 1
        elif table1_sort:
            self.active_table = 1
        elif table2_sort:
            self.active_table = 2
        if not table1_sort:
            table1_sort = '-ntmatches'
        if not table2_sort:
            table2_sort = '-ntmatches'
        self.tables = [
            NTTeamsStatsTable(
                NTTeamsStats.objects.filter(countryid=self.country.code, stat_type="team").order_by(table1_sort),
                order_by=table1_sort,
            ),
            NTTeamsStatsTable(
                NTTeamsStats.objects.filter(countryid=self.country.code, stat_type="youth").order_by(table2_sort),
                order_by=table2_sort,
            ),
        ]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional variables to the context
        context["page_title"] = _("Best Players All Time Stats Teams")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        context["submenu"] = 'stats_teams'
        context["active_table"] = self.active_table  # Add active_table to context
        return context


class BestPlayersTeamStats(TemplateView):
    template_name = "ntdb/players-best-team.html"
    context_object_name = "objects"
    country = None  # Initialize class attribute to store country_name
    age_filter = None


    def dispatch(self, request, *args, **kwargs):

        self.country_name = kwargs.get("country_name")
        self.team_id = kwargs.get("team_id")
        self.country = (
            Country.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower=self.country_name.lower())
            .first()
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = Team.objects.filter(id=self.team_id).first()
        team_stats = NTTeamsStats.objects.filter(countryid=self.country.code, stat_type="team", teamid=self.team_id).order_by("-ntmatches").first()
        youth_stats = NTTeamsStats.objects.filter(countryid=self.country.code, stat_type="youth", teamid=self.team_id).order_by("-ntmatches").first()
        if isinstance(team_stats.json_data, str):
            team_stats.json_data = json.loads(team_stats.json_data)
        if isinstance(youth_stats.json_data_youth, str):
            youth_stats.json_data_youth = json.loads(youth_stats.json_data_youth)
        # Add additional variables to the context
        context["page_title"] = _("Best Players All Time Stats Teams")
        context["page_siblings"] = NTDB_SUB_MENU
        context["menu_type"] = "NTDB"
        context["country"] = self.country
        context["submenu"] = 'stats_teams'
        context["team"] = team
        context["team_stats"] = team_stats
        context["youth_stats"] = youth_stats
        context["active_table"] = 1
        return context



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
            WingArchivePlayerTable(
                return_distinct_all_time_records_by_position(
                    "WING", self.country, start_age, end_age
                ),
                order_by="-wing_points",
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
        context["submenu"] = 'all'
        context["active_table"] = 1
        return context

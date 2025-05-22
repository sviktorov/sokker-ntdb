from django.db import models
from django.utils.translation import gettext_lazy as _
from sokker_base.models import Team
from .utils import DRAW_STATUS_CHOICES, CUP_STATUS_CHOICES, WEEKDAY_CHOICES
from sokker_base.models import Country

class CupCategory(models.Model):
    id = models.AutoField(primary_key=True)  # Assuming c_id is an auto-incrementing ID
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Cup(models.Model):
    id = models.AutoField(primary_key=True)  # Assuming c_id is an auto-incrementing ID
    category = models.ForeignKey(
        CupCategory, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    # New header_image field
    header_image = models.ImageField(upload_to="header_images/", null=True, blank=True, help_text=_("Header image for the cup 1920x300px"))
    forum_link = models.CharField(max_length=255, null=True, blank=True, help_text=_("Forum link for the cup"))
    c_name = models.CharField(max_length=255, help_text=_("Name of the cup"))
    c_edition = models.IntegerField(null=True, blank=True, help_text=_("Edition of the cup"))
    c_flow = models.IntegerField(null=True, blank=True, default=1, help_text=_("Flow of the cup if few cups are splited in different flows"))
    c_teams = models.IntegerField(null=True, blank=True, help_text=_("Total number of teams in the cup"))
    c_groups = models.IntegerField(null=True, blank=True, help_text=_("Number of groups in the cup"))
    c_g_winners = models.IntegerField(
        null=True, blank=True, help_text=_("Total Number of teams proceeding to the next round")
    )  # Assuming this is the number of group winners
    c_games_groups = models.IntegerField(null=True, blank=True, help_text=_("Number of games in group stage between teams"))
    c_games = models.IntegerField(null=True, blank=True, help_text=_("Number of games in the playoffs"))
    c_status = models.CharField(
        max_length=50,
        choices=CUP_STATUS_CHOICES,
        blank=True,
        null=True,
        default=''
    )

    c_draw_status = models.CharField(
        max_length=50,
        choices=DRAW_STATUS_CHOICES,
        blank=True,
        null=True,
        default=''
    )
    c_draw_date = models.DateTimeField(null=True, blank=True, default=None)
    c_notes = models.TextField(null=True, blank=True)  # Assuming this can be nullable
    c_active = models.BooleanField(default=False)  # Assuming this is a boolean field
    is_cl = models.BooleanField(default=False, help_text=_("If the cup is a CL format"))
    c_start_date = models.DateTimeField(null=True, blank=True, default=None, help_text=_("Start date of the cup 1 round")) 
    match_days = models.JSONField(
        default=list,
        help_text="List of weekdays when matches can be played (0=Monday, 6=Sunday)",
    )
    rating_limit = models.FloatField(null=True, blank=True, default=None, help_text=_("Rating limit for the cup"))
    looser_playoffs = models.BooleanField(default=False, help_text=_("If the loosers in groups play separate playoffs"))
    draw_playoffs = models.BooleanField(default=False, help_text=_("If the playoffs have draw"))
    def __str__(self):
        return self.c_name


class CupTeams(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    g_id = models.IntegerField()
    pot_id = models.IntegerField(null=True, blank=True, default=0)
    rating = models.FloatField(null=True, blank=True, default=0)
    cl_draw = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"

    class Meta:
        verbose_name_plural = _("Cup Teams")


class CupDraw(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True, default=0)
    g_id = models.IntegerField()

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id_h = models.ForeignKey(
        Team,
        related_name="home_team_base",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    t_id_v = models.ForeignKey(
        Team,
        related_name="away_team_base",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    g_status = models.CharField(max_length=50, null=True, blank=True, default="")
    group_id = models.CharField()
    goals_home = models.IntegerField(null=True, blank=True)
    goals_away = models.IntegerField(null=True, blank=True)
    rating_home = models.FloatField(null=True, blank=True, default=None)
    rating_away = models.FloatField(null=True, blank=True, default=None)
    cup_round = models.CharField(max_length=50)
    matchID = models.CharField(max_length=255)
    playoff_position = models.CharField(max_length=50, null=True, blank=True)
    has_stats = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Game {self.id}: {self.t_id_h} vs {self.t_id_v} - Status: {self.g_status}"
        )

    def score_display(self):
        if self.goals_home is not None and self.goals_away is not None:
            return f"{self.goals_home} - {self.goals_away}"
        return "N/A"
    
    def score_display_invert(self):
        if self.goals_home is not None and self.goals_away is not None:
            return f"{self.goals_away} - {self.goals_home}"
        return "N/A"

    def score_display_by_team(self, team_id):
        if self.t_id_h.id == team_id:
            return self.score_display()
        else:
            return self.score_display_invert()
    
    def score_points_by_team(self, team_id):
        if self.t_id_h.id == team_id:
            return self.home_points()
        else:
            return self.away_points()

    def score_display_by_team_as_class(self, team_id):
        if self.t_id_h.id == team_id:
            return self.home_status()
        else:
            return self.away_status()
    
    def away_points(self):
        if self.goals_home is None or self.goals_away is None:
            return 0
        if self.goals_away > self.goals_home:
            return 3
        if self.goals_home == self.goals_away:
            return 1
        return 0

    def home_points(self):
        if self.goals_home is None or self.goals_away is None:
            return 0
        if self.goals_home > self.goals_away:
            return 3
        if self.goals_home == self.goals_away:
            return 1
        return 0

    def home_status(self):
        if self.goals_home is None or self.goals_away is None:
            return _("N/A")
        if self.goals_home > self.goals_away:
            return _("win")
        if self.goals_home == self.goals_away:
            return _("draw")
        return _("loss")

    def away_status(self):
        if self.goals_home is None or self.goals_away is None:
            return _("N/A")
        if self.goals_away > self.goals_home:
            return _("win")
        if self.goals_away == self.goals_home:
            return _("draw")
        return _("loss")


class RankGroups(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_rank_arcades", on_delete=models.CASCADE
    )
    games = models.IntegerField(null=True, blank=True)
    g_id = models.IntegerField(null=True, blank=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    wins = models.IntegerField(null=True, blank=True)
    loose = models.IntegerField(null=True, blank=True)
    gdif = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    gscored = models.IntegerField(null=True, blank=True)
    grecieved = models.IntegerField(null=True, blank=True)
    draw = models.IntegerField(null=True, blank=True)
    qualified = models.CharField(max_length=50)

    def __str__(self):
        return f"Team {self.id}: {self.t_id}  - Cup: {self.c_id} points {self.points}"

    class Meta:
        verbose_name_plural = _("Rank Groups")


class Medals(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_medal_arcades", on_delete=models.CASCADE
    )
    position_1 = models.IntegerField(null=True, blank=True)
    position_2 = models.IntegerField(null=True, blank=True)
    position_3 = models.IntegerField(null=True, blank=True)
    position_4 = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Medals")


class Winners(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.IntegerField(null=True, blank=True)
    cup_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    team_id = models.ForeignKey(
        Team, related_name="team_winners", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = _("Winners")


class RankAllTime(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_rank_all_time", on_delete=models.CASCADE
    )
    games = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(null=True, blank=True)
    loose = models.IntegerField(null=True, blank=True)
    gdif = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    gscored = models.IntegerField(null=True, blank=True)
    grecieved = models.IntegerField(null=True, blank=True)
    draw = models.IntegerField(null=True, blank=True)
    c_flow = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return f"Team {self.id}: {self.t_id}  - Cup: {self.c_id} points {self.points}"

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return f"Player {self.id}: {self.name} - Team: {self.team_id}"

class GameDetails(models.Model):
    id = models.AutoField(primary_key=True)
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_home = models.BooleanField(default=False)
    timeOnHalf = models.IntegerField(null=True, blank=True)
    timePossession = models.IntegerField(null=True, blank=True)
    shots = models.IntegerField(null=True, blank=True)
    fouls = models.IntegerField(null=True, blank=True)
    yellowCards = models.IntegerField(null=True, blank=True)
    redCards = models.IntegerField(null=True, blank=True)
    offsides = models.IntegerField(null=True, blank=True)
    effShoot = models.IntegerField(null=True, blank=True)
    effPass = models.IntegerField(null=True, blank=True)
    effTackle = models.IntegerField(null=True, blank=True)
   
    
    def __str__(self):
        return f"Game Details {self.id}: {self.game_id} - {self.team_id} - {self.is_home}"
    
    class Meta:
        verbose_name_plural = _("Game Details")

class CupGameStats(models.Model):
    id = models.AutoField(primary_key=True)
    goals = models.IntegerField(null=True, blank=True)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    assists = models.IntegerField(null=True, blank=True)
    red_cards = models.IntegerField(null=True, blank=True)
    yellow_cards = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Goal {self.id}:  - {self.player_id}  - {self.game_id} - {self.team_id}"
    
    class Meta:
        verbose_name_plural = _("Cup Game Stats")

class PlayoffPots(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    pot_id = models.IntegerField(null=True, blank=True)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    flow = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Playoff Pot {self.id}: {self.c_id} - {self.pot_id} - {self.t_id}"  
    
    class Meta:
        verbose_name_plural = _("Playoff Pots")

class PlayoffDraw(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    pot_id = models.IntegerField(null=True, blank=True)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    draw_id = models.IntegerField(null=True, blank=True)
    flow = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"Playoff Draw {self.id}: {self.c_id} - {self.pot_id} - {self.t_id} - {self.draw_id}"

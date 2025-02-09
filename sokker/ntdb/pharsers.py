from django.utils import timezone
from sokker_base.models import Country, Team


def parser_team(response, team):
    if response.status_code == 200:
        data = response.json()
        team.name = data["name"]
        code = data["country"]["code"]
        country = Country.objects.filter(code=code).first()
        if not country:
            return False
        team.country = country
        return team
    return team


def parser_player(response, player):
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
        player.ntmatches = nationalStats["matches"]
        team_object_youth = Team.objects.filter(id=youthTeamId).first()
        if team_object_youth:
            player.youthteamid = team_object_youth
        else:
            player.youthteamid = None
        player.injurydays = injury["daysRemaining"]
        flag = False
        # hidden skills
        if skills.get("keeper"):
            player.skillkeeper = skills["keeper"]
            flag = True
        if skills.get("defending"):
            player.skilldefending = skills["defending"]
            flag = True
        if skills.get("pace"):
            player.skillpace = skills["pace"]
            flag = True
        if skills.get("playmaking"):
            player.skillplaymaking = skills["playmaking"]
            flag = True
        if skills.get("passing"):
            player.skillpassing = skills["passing"]
            flag = True
        if skills.get("technique"):
            player.skilltechnique = skills["technique"]
            flag = True
        if skills.get("striker"):
            player.skillscoring = skills["striker"]
        if skills.get("stamina"):
            player.skillstamina = skills["stamina"]
            flag = True
        if flag:
            player.modified = timezone.now()
        player.daily_update = timezone.now()
    return player

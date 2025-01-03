from itertools import combinations, permutations

import random
import os
import sys
import json
from functools import lru_cache
from datetime import datetime, timedelta

# Increase the recursion depth to a higher value (e.g., 5000)
sys.setrecursionlimit(130000)

CL_TEAMS = [
        list(range(1, 10)),    # Pot 1: Teams 1 to 9
        list(range(10, 19)),   # Pot 2: Teams 10 to 18
        list(range(19, 28)),   # Pot 3: Teams 19 to 27
        list(range(28, 37)),   # Pot 4: Teams 28 to 36
    ]


def get_next_monday_or_saturday(start_date):
    """
    Get the next Monday or Saturday from the given date.

    Args:
        start_date (datetime): The date to start from.

    Returns:
        datetime: The next Monday or Saturday.
    """
    days_ahead_monday = (7 - start_date.weekday() + 0) % 7  # 0 for Monday
    days_ahead_saturday = (7 - start_date.weekday() + 5) % 7  # 5 for Saturday

    if days_ahead_monday == 0:  # If today is Monday
        days_ahead_monday = 7
    if days_ahead_saturday == 0:  # If today is Saturday
        days_ahead_saturday = 7

    next_monday = start_date + timedelta(days=days_ahead_monday)
    next_saturday = start_date + timedelta(days=days_ahead_saturday)

    return min(next_monday, next_saturday)


# Function to save fixtures to a file
def save_fixtures_to_file(fixtures, filename="fixtures.json"):
    with open(filename, "w") as file:
        json.dump(fixtures, file)
    print(f"Fixtures saved to {filename}")

# Function to load fixtures from a file if it exists
def load_fixtures_from_file(filename="fixtures.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            fixtures = json.load(file)
        print(f"Fixtures loaded from {filename}")
        return fixtures
    return None

def generate_team_pairs(team, other_teams, is_home):
    """
    Generate all pairs where the specified team is either the first or second element.
    
    Args:
        team (str): The specific team to include in pairs.
        other_teams (list): A list of other teams to pair with.
        
    Returns:
        list: A list of tuples representing the pairs.
    """
    # Create pairs where team is the first or second element
    if is_home:
        pairs = [(team, other_team) for other_team in other_teams] 
    else:
        pairs = [(other_team, team) for other_team in other_teams]
    return pairs

@lru_cache(maxsize=None)
def pot_for_team(team):
    pots = CL_TEAMS
    counter=0
    for pot in pots:
        if team in pot:
            return counter
        counter=counter+1
    return False

def pairs_team_pot(pot, team, is_home):
    pots = CL_TEAMS
    return generate_team_pairs(team, pots[pot], is_home)

def generate_round_robin_fixtures(number_teams):
    teams = list(range(1, number_teams + 1))  # Convert range to list
    rounds = []
    all_previous_matches = set()  # To store already played pairs

    for round_num in range(number_teams-1):  # Assuming 7 rounds for 8 teams
        round_fixtures = []
        random.shuffle(teams)  # Shuffle teams to randomize matchups
        
        # Create matchups for this round by pairing up the teams
        for i in range(0, len(teams), 2):
            match = tuple(sorted([teams[i], teams[i+1]]))  # Sort to avoid reversing pairs
            
            # Ensure that the match has not already occurred in previous rounds
            while match in all_previous_matches:
                random.shuffle(teams)  # Reshuffle if there is a repetition
                match = tuple(sorted([teams[i], teams[i+1]]))
            
            round_fixtures.append([teams[i], teams[i+1]])
            all_previous_matches.add(match)  # Add the current match to the set
        
        rounds.append(round_fixtures)

    return rounds




def generate_fixtures_cl_32():
    """
    Generate fixtures for 32 teams in 8 groups of 4 teams.
    The first 7 rounds will be inter-group, and the last round (round 8) will be intra-group games.
    
    Returns:
        list: A list of 8 rounds, each round containing 16 games in the format [round, home_id, away_id].
    """
    # Step 1: Split 32 teams into 4 pots, each with 8 teams
    pots_fixtures = generate_round_robin_fixtures(8)

    pots = [
        list(range(1, 5)),    # Pot 1: Teams 1 to 4
        list(range(5, 9)),    # Pot 2: Teams 5 to 8
        list(range(9, 13)),   # Pot 3: Teams 9 to 12
        list(range(13, 17)),   # Pot 4: Teams 13 to 16
        list(range(17, 21)),  # Pot 5: Teams 17 to 20
        list(range(21, 25)),  # Pot 6: Teams 21 to 24
        list(range(25, 29)),   # Pot 7: Teams 25 to 28
        list(range(29, 33))   # Pot 8: Teams 29 to 32
    ]
    rounds = []
    round_number = 0
    for round  in pots_fixtures:
        round_number=round_number+1
        games = []
        for pair in round:
            pot_home = pots[pair[0]-1]
            pot_away = pots[pair[1]-1]
            paired = list(zip(pot_home, pot_away))
            # Print the pairs
            for pair in paired:
                games.append([round_number, pair[0], pair[1]])
        rounds.append(games)


    round_number = 8
    games = []
    for pot in pots:
        random.shuffle(pot)
        games.append([round_number, pot[0], pot[1]])
        games.append([round_number, pot[2], pot[3]])
    rounds.append(games)
    return rounds

def generate_unique_fixtures(teams, num_rounds, num_pairs_per_round):

    matrix_teams = []
    for pot in CL_TEAMS:
        for team in pot:
            matrix_teams.append(
                {
                    team: {
                        "home": 0,
                        "away": 0,
                        "pot1": 0,
                        "pot2": 0,
                        "pot3": 0,
                        "pot4": 0,
                    }
                }
            )   
    # Generate all possible pairs
    all_possible_pairs = list(permutations(teams, 2))
    print(len(all_possible_pairs))
    random.shuffle(all_possible_pairs)  # Shuffle to introduce randomness
    # Keep track of used pairs
    used_pairs = set()
    rounds = []

    for round_num in range(num_rounds):
        round_pairs = []
        available_pairs = [pair for pair in all_possible_pairs if pair not in used_pairs]

        # Generate pairs for the current round
        while len(round_pairs) < num_pairs_per_round and available_pairs:
            pair = available_pairs.pop(0)  # Pick the first pair
            # Check if teams in the pair are already used in the current round
            if any(pair[0] in p or pair[1] in p for p in round_pairs):
                continue
        
        round_pairs = []
        pairs_pool = [pair for pair in all_possible_pairs if pair not in used_pairs]
        # Sort pairs based on a heuristic (e.g., least used teams)
        if round_num == 0:
            random.shuffle(pairs_pool)  # Shuffle to pick pairs randomly
        else:
            pairs_pool.sort(key=lambda pair: (
                matrix_teams[pair[0] - 1][pair[0]]["home"] + 
                matrix_teams[pair[1] - 1][pair[1]]["away"]
            ))
        
        # Pick unique pairs for this round
        for pair in pairs_pool:
            if len(round_pairs) >= num_pairs_per_round:
                break
            # Ensure no team is reused in this round
            if any(pair[0] in p or pair[1] in p for p in round_pairs):
                continue

            matrix_teams[pair[0] - 1][pair[0]]["home"] = matrix_teams[pair[0] - 1][pair[0]]["home"] +1
            matrix_teams[pair[1] - 1][pair[1]]["away"] = matrix_teams[pair[1] - 1][pair[1]]["away"] +1

            oposit_pair = (pair[1], pair[0])
            round_pairs.append(pair)
            used_pairs.add(pair)
            used_pairs.add(oposit_pair)
            pot_home = pot_for_team(pair[0])
            pot_away = pot_for_team(pair[1])
            home_pairs = pairs_team_pot(pot_home, pair[1], False)
            away_pairs = pairs_team_pot(pot_away, pair[0], True)

            for p in home_pairs:
                used_pairs.add(p)
            for p in away_pairs:
                used_pairs.add(p)

        
        # Check if we successfully generated the required pairs
        if len(round_pairs) < num_pairs_per_round:
            break
        
        round_games = []
        for pair in round_pairs:
            round_games.append([round_num+1, pair[0], pair[1]])
        rounds.append(round_games)
    
    if len(rounds) < num_rounds:
        print("Retrying fixture generation due to insufficient rounds.")
        return generate_unique_fixtures(teams, num_rounds, num_pairs_per_round)

    
    return rounds


def generate_fixtures_cl():
    """
    Generate fixtures for 36 teams in 9 teams of 4 teams.
    The first 7 rounds will be inter-group, and the last round (round 8) will be intra-group games.
    
    Returns:
        list: A list of 8 rounds, each round containing 16 games in the format [round, home_id, away_id].
    """
    seed = random.randint(1, 3)
    filename = "cl_fixtures_{}.json".format(seed)
    fixtures = load_fixtures_from_file(filename)
    if fixtures:
        return fixtures, filename

    matrix_teams = []
    for pot in CL_TEAMS:
        for team in pot:
            matrix_teams.append(
                {
                    team: {
                        "home":0,
                        "away":0,
                        "pot1":0,
                        "pot2":0,
                        "pot3":0,
                        "pot4":0,
                    }
                }
            )

    fixtures = generate_unique_fixtures(list(range(1, 37)), 8, 18)

    for rounds in fixtures:
        uniq_teams = []
        round_num =0
        for game in rounds:
            round_num = game[0]
            matrix_teams[game[1]-1][game[1]]["home"] = matrix_teams[game[1]-1][game[1]]["home"]+ 1
            matrix_teams[game[2]-1][game[2]]["away"] = matrix_teams[game[2]-1][game[2]]["away"]+1
            p = pot_for_team(game[2])
            pot_index="pot{}".format(p+1)
            matrix_teams[game[1]-1][game[1]][pot_index] = matrix_teams[game[1]-1][game[1]][pot_index] +1
            if matrix_teams[game[1]-1][game[1]][pot_index]>2:
                print("more than 2 games against {} for team {}".format(pot_index,game[1]))    
            p = pot_for_team(game[1])
            pot_index="pot{}".format(p+1)
            matrix_teams[game[2]-1][game[2]][pot_index] = matrix_teams[game[2]-1][game[2]][pot_index] +1
            if matrix_teams[game[2]-1][game[2]][pot_index]>2:
                print("more than 2 games against {} for team {}".format(pot_index,game[2])) 
            if game[1] not in uniq_teams: 
                uniq_teams.append(game[1])
            if game[2] not in uniq_teams: 
                uniq_teams.append(game[2])
            if matrix_teams[game[1]-1][game[1]]["home"] >4: 
                print("error more 4 home  games")
            if matrix_teams[game[2]-1][game[2]]["away"]>4:
                print("error more 4 away  games")
        if not len(uniq_teams) == 36:
            print("error uniq teams round {}".round_num)
    save_fixtures_to_file(fixtures, filename)
        
    return fixtures, filename
   




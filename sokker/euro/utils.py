from datetime import datetime, timedelta

def calculate_round_date(cup_round: int, start_date: datetime) -> datetime:
    if cup_round <= 1:
        return start_date
    
    # Add 7 days for each round after round 1
    days_to_add = (cup_round - 1) * 7
    return start_date + timedelta(days=days_to_add)

def format_round_date(cup_round: int, start_date: datetime, format_str: str = "%Y-%m-%d") -> str:
    round_date = calculate_round_date(cup_round, start_date)
    return round_date.strftime(format_str)
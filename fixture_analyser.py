import pandas as pd
import numpy as np

pd.options.display.float_format = "{:,.2f}".format

def get_attacking_points_mult(fixtures: pd.DataFrame, team: str, teams_df: pd.DataFrame, fixture_weighting: float = 1.0) -> pd.DataFrame:
    """
    Gets a team's fixtures and calculates how difficult (or easy) it would be for attacking players to get points by comparing attacking quality to opponent's defensive quality. Evenly matched returns a 1, >1 means more likely to get points.

    Arguments:
        - fixtures: the dataframe of fixtures
        - team: the team whose fixtures are to be checked
        - teams_df: dataframe of teams containing attacking and defensive quality
        - fixture_weighting: how much value fixtures should be given

    Returns:
        A dataframe of the attacking difficulty of each upcoming fixture
    """
    teams_fixtures: pd.DataFrame = fixtures[team]

    opp_def_qual: pd.DataFrame = teams_fixtures.apply(lambda t: teams_df.at[t, "Defensive Quality"])
    self_att_qual: float = teams_df.at[team, "Attacking Quality"]
    difference: pd.DataFrame = opp_def_qual.apply(lambda d: self_att_qual - d)

    att_points_mult: pd.DataFrame = difference.apply(lambda x: x * fixture_weighting + 1)

    att_points_mult.index = att_points_mult.index + 1 # Adjust index to match gameweek convention

    return att_points_mult

def get_defending_points_mult(fixtures: pd.DataFrame, team: str, teams_df: pd.DataFrame, fixture_weighting: float = 1.0) -> pd.DataFrame:
    """
    Gets a team's fixtures and calculates how difficult (or easy) it would be for defending players to get points by comparing defending quality to opponent's attacking quality. Evenly matched returns a 1, >1 means more likely to get points.

    Arguments:
        - fixtures: the dataframe of fixtures
        - team: the team whose fixtures are to be checked
        - teams_df: dataframe of teams containing attacking and defensive quality
        - fixture_weighting: how much value fixtures should be given

    Returns:
        A dataframe of the attacking difficulty of each upcoming fixture
    """
    teams_fixtures: pd.DataFrame = fixtures[team]

    opp_att_qual: pd.DataFrame = teams_fixtures.apply(lambda t: teams_df.at[t, "Attacking Quality"])
    self_def_qual: float = teams_df.at[team, "Defensive Quality"]
    difference: pd.DataFrame = opp_att_qual.apply(lambda d: self_def_qual - d)

    def_points_mult: pd.DataFrame = difference.apply(lambda x: x * fixture_weighting + 1)

    def_points_mult.index = def_points_mult.index + 1 # Adjust index to match gameweek convention

    return def_points_mult

def get_upcoming_attacking_mult(fixtures: pd.DataFrame, team: str, teams_df: pd.DataFrame, look_ahead: int, starting_gameweek: int, fixture_weighting: float = 1.0) -> float:
    """
    Get overall multipler for upcoming set of fixtures

    Arguments:
        - fixtures: the dataframe of fixtures
        - team: the team whose fixtures are to be checked
        - teams_df: dataframe of teams containing attacking and defensive quality
        - look_ahead: how many future fixtures to consider
        - starting_gameweek: gameweek to start considering
        - fixture_weighting: how much value fixtures should be given

    Returns:
        Sum of attacker multipliers for upcoming fixtures
    """

    attacking_points: pd.DataFrame = get_attacking_points_mult(fixtures, team, teams_df, fixture_weighting)

    summed_mult: float = attacking_points.where((attacking_points.index >= starting_gameweek) & (attacking_points.index <= starting_gameweek + look_ahead)).sum()

    return summed_mult

def get_upcoming_defending_mult(fixtures: pd.DataFrame, team: str, teams_df: pd.DataFrame, look_ahead: int, starting_gameweek: int, fixture_weighting: float = 1.0) -> float:
    """
    Get overall multipler for upcoming set of fixtures

    Arguments:
        - fixtures: the dataframe of fixtures
        - team: the team whose fixtures are to be checked
        - teams_df: dataframe of teams containing attacking and defensive quality
        - look_ahead: how many future fixtures to consider
        - starting_gameweek: gameweek to start considering
        - fixture_weighting: how much value fixtures should be given

    Returns:
        Sum of defender multipliers for upcoming fixtures
    """

    defending_points: pd.DataFrame = get_defending_points_mult(fixtures, team, teams_df, fixture_weighting)

    summed_mult: float = defending_points.where((defending_points.index >= starting_gameweek) & (defending_points.index <= starting_gameweek + look_ahead)).sum()

    return summed_mult

def get_all_upcoming_multipliers(fixtures: pd.DataFrame, teams_df: pd.DataFrame, look_ahead: int, starting_gameweek: int, fixture_weighting: float = 1.0) -> pd.DataFrame:
    """
    Calculates upcoming attacking and defending multipliers for every team in the given fixture range.

    Arguments:
        - fixtures: the dataframe of fixtures
        - teams_df: dataframe of teams containing attacking and defensive quality
        - look_ahead: how many future fixtures to consider
        - starting_gameweek: gameweek to start considering
        - fixture_weighting: how much value fixtures should be given

    Returns:
        Dataframe with teams and their attacking and defending multipliers
    """

    team_multipliers = teams_df

    team_multipliers["Attacking Multiplier"] = team_multipliers.apply(lambda row: get_upcoming_attacking_mult(fixtures, row.name, teams_df, look_ahead, starting_gameweek, fixture_weighting), axis=1)
    team_multipliers["Defending Multiplier"] = team_multipliers.apply(lambda row: get_upcoming_defending_mult(fixtures, row.name, teams_df, look_ahead, starting_gameweek, fixture_weighting), axis=1)

    return team_multipliers[["Attacking Multiplier", "Defending Multiplier"]]

def get_player_post_quality(player_row: pd.DataFrame, multiplier_df: pd.DataFrame) -> float:
    """
    Multiplies the applicable mutliplier to a player

    Arguments:
        - player_row: row of the player dataframe for multiplier to be applied
        - multiplier_df: dataframe of all multipliers
    
    Returns:
        The "post quality" of the player (quality * multiplier)
    """

    team = player_row["Team"]
    pos = player_row["Pos."]

    if pos in ["GKP", "DEF"]:
        post_quality = multiplier_df.loc[team]["Defending Multiplier"] * player_row["Quality"]
    else:
        post_quality = multiplier_df.loc[team]["Attacking Multiplier"] * player_row["Quality"]

    return post_quality

def apply_fixture_multipliers(players: pd.DataFrame, fixtures: pd.DataFrame, teams_df: pd.DataFrame, look_ahead: int, starting_gameweek: int, fixture_weighting: float = 1.0) -> pd.DataFrame:
    """
    Calculates the 'Post Quality' of each player by multiplying the attacking or defending multiplier to a player's quality

    Arguments:
        - players: the dataframe of players
        - fixtures: the dataframe of fixtures
        - teams_df: dataframe of teams containing attacking and defensive quality
        - look_ahead: how many future fixtures to consider
        - starting_gameweek: gameweek to start considering
        - fixture_weighting: how much value fixtures should be given

    Returns:
        Dataframe with players and their post quality
    """

    multipliers = get_all_upcoming_multipliers(fixtures, teams_df, look_ahead, starting_gameweek, fixture_weighting)

    post_players = players.copy()
    post_players["Post Quality"] = players.apply(lambda player_row: get_player_post_quality(player_row, multipliers), axis=1)

    post_players = post_players[['Post Quality', 'Quality', 'Pos.', 'Team', 'Price']]
    return post_players.sort_values("Post Quality", ascending=False)

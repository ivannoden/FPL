import pandas as pd
pd.options.display.float_format = "{:,.2f}".format

def read_spreadsheet(filename: str, player_sheets: int, player_sheet_offset: int = 0, teams_name: str = "Teams", fixtures_name: str = "Fixtures", games_name: str = "Games") -> dict[str, pd.DataFrame]:
    """
    Reads spreadsheet and return data on players, teams, fixtures and games

    Arguments:
        - filename: the filename of the spreadsheet
        - player_sheets: the number of sheets for players in the spreadsheet
        - player_sheet_offset: how many sheets in the player sheets start
        - teams_name: the name of the sheet for teams
        - fixtures_name: the name of the sheet for fixtures
        - games_name: the name of the sheet for games

    Returns:
        A dictionary containing all dataframes for "Players", "Teams", "Fixtures", and "Games"
    
    """

    player_dfs: pd.DataFrame = pd.read_excel(filename, sheet_name=[i for i in range(player_sheet_offset, player_sheets)], index_col=0) #Get dataframe for each sheet containg players
    players: pd.DataFrame = pd.concat([player_dfs[i] for i in range(player_sheets)]) #Concatenate players into one dataframe

    #Create teams dataframe
    teams_df: pd.DataFrame = pd.read_excel(filename, sheet_name=teams_name, index_col=0)
    teams: pd.DataFrame = teams_df[["Attacking Quality", "Defensive Quality"]]

    #Create games dataframe
    games: pd.DataFrame = pd.read_excel(filename, sheet_name=games_name)

    #Create fixtures dataframe
    fixtures: pd.DataFrame = pd.read_excel(filename, sheet_name=fixtures_name)

    df_dict: dict[str, pd.DataFrame] = {"Players": players, "Teams": teams, "Games": games, "Fixtures": fixtures}

    return df_dict

def simplify_players(players: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a 'cleaner' dataframe for players containing only important information

    Arguments:
        - players: player dataframe to be cleaned up

    Returns:
        Cleaned up dataframe 
    """

    clean_players = players[["Quality", "Pos.", "Team", "Price"]]
    return clean_players

def get_upcoming_gameweek(games: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the upcoming gameweek from games dataframe

    Arguments:
        - games: the dataframe of games from read_spreadsheet

    Returns:
        Current gameweek
    """

    return games["GW"].max() + 1

def get_upcoming_fixtures(fixtures: pd.DataFrame, team: str, look_ahead: int, starting_gameweek: int) -> pd.DataFrame:
    """
    Get the next n fixtures after the given gameweek from a given team

    Arguments:
        - fixtures: dataframe of fixtures
        - team: the team to find fixtures for
        - look_ahead: number of gameweeks to consider
        - starting_gameweek: the gameweek to start looking from

    Returns:
        Dataframe of that team's fixtures in the given time slot
    """

    team_fixtures: pd.DataFrame = fixtures[["GW", team]]
    gws: pd.DataFrame = team_fixtures["GW"]
    teams: pd.DataFrame = team_fixtures[team]

    upcoming_fixtures: pd.DataFrame = team_fixtures.loc[gws <= starting_gameweek + look_ahead]
    upcoming_fixtures: pd.DataFrame = upcoming_fixtures.loc[gws >= starting_gameweek]
    upcoming_fixtures: pd.DataFrame = upcoming_fixtures.loc[teams.notnull()]

    return upcoming_fixtures[team]
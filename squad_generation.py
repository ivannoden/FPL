import pandas as pd

def gen_squad(players: pd.DataFrame, cheapest_player: float) -> pd.DataFrame:
    """
    Generate the squad of 15 that fit the FPL criteria and produce the highest quality

    Arguments:
        - players: dataframe of players to consider
        - cheapest_player: ensures that enough budget is left to purchase players all of this price

    Returns:
        Dataframe of a squad of chosen players
    """


    squad = pd.DataFrame(columns=["Post Quality", "Quality", "Pos.", "Team", "Price"], index=players.index)
    squad.drop_duplicates(inplace=True)

    allowed_per_position = {"GKP": 2, "DEF": 5, "MID": 5, "FWD": 3}

    size = 0
    for idx, row in players.iterrows():

        squad_price = squad["Price"].sum()
        
        overbudget = False
        if size != 0:
            overbudget = (100 - (squad_price + row["Price"]))/(15 - size) < cheapest_player

        try:
            team_count = squad["Team"].value_counts().loc[row["Team"]]
        except KeyError:
            team_count = 0

        try:
            pos_count = squad["Pos."].value_counts().loc[row["Pos."]]
        except KeyError:
            pos_count = 0

        if overbudget:
            next
        elif team_count == 3:
            next
        elif pos_count == allowed_per_position[row["Pos."]]:
            next

        else:
            size = size + 1
            squad.loc[idx] = row

        if size >= 15:
            break

    return squad.dropna()


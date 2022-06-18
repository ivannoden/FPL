import reader as r
import fixture_analyser as fa

def main() -> None:
    spreadsheet = "FPL.xlsx"

    dataframes = r.read_spreadsheet(spreadsheet, 21)

    players_verbose = dataframes["Players"]
    teams = dataframes["Teams"]
    games = dataframes["Games"]
    fixtures = dataframes["Fixtures"]

    players = r.simplify_players(players_verbose)

    upcoming_gameweek = r.get_upcoming_gameweek(games)

    print(fa.apply_fixture_multipliers(players, fixtures, teams, 5, upcoming_gameweek))

if __name__ == "__main__":
    main()
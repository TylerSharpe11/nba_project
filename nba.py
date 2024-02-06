from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, commonteamroster
import pandas as pd

# Function to fetch and compare player statistics
def fetch_and_compare_player_stats(player_full_name, team_full_name, season='2023', points_threshold=28):
    # Get player ID
    player_info = [player for player in players.get_players() if player['full_name'].lower() == player_full_name.lower()]
    if not player_info:
        print(f"No player found with the name {player_full_name}.")
        return
    player_id = player_info[0]['id']
    
    # Get team ID
    team_info = [team for team in teams.get_teams() if team['full_name'].lower() == team_full_name.lower()]
    if not team_info:
        print(f"No team found with the name {team_full_name}.")
        return
    team_id = team_info[0]['id']

    # Fetch the roster for the team for the specified season
    roster = commonteamroster.CommonTeamRoster(season=season, team_id=team_id)
    roster_df = roster.get_data_frames()[0]

    # Fetch game logs for the specified player for the season
    player_gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    player_df = player_gamelog.get_data_frames()[0]

    # Identify games where the specified player scored more than the points threshold
    high_scoring_games = player_df[player_df['PTS'] > points_threshold]['Game_ID'].unique()

    # Prepare a list for accumulating player data
    player_data = []

    # For each player on the roster, fetch their game logs and calculate averages
    for index, row in roster_df.iterrows():
        player_id = row['PLAYER_ID']
        player_name = row['PLAYER']
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = gamelog.get_data_frames()[0]
        
        # Filter for high scoring games
        df_high_scoring = df[df['Game_ID'].isin(high_scoring_games)]
        
        # Calculate average assists, rebounds, and points in those games and overall
        avg_assists_overall = df['AST'].mean()
        avg_rebounds_overall = df['REB'].mean()
        avg_points_overall = df['PTS'].mean()
        avg_minutes_overall = df['MIN'].mean()
        if avg_minutes_overall < 15:
            continue
        
        
        avg_assists_high_scoring = df_high_scoring['AST'].mean() if not df_high_scoring.empty else 0
        avg_rebounds_high_scoring = df_high_scoring['REB'].mean() if not df_high_scoring.empty else 0
        avg_points_high_scoring = df_high_scoring['PTS'].mean() if not df_high_scoring.empty else 0
        
        # Calculate percentage changes
        pct_change_assists = ((avg_assists_high_scoring - avg_assists_overall) / avg_assists_overall) * 100 if avg_assists_overall else 0
        pct_change_rebounds = ((avg_rebounds_high_scoring - avg_rebounds_overall) / avg_rebounds_overall) * 100 if avg_rebounds_overall else 0
        pct_change_points = ((avg_points_high_scoring - avg_points_overall) / avg_points_overall) * 100 if avg_points_overall else 0
        
        # Add to the list as a dictionary
        player_data.append({
            'Player Name': player_name,
            'Normal Average Assists': avg_assists_overall,
            'Assists with High PTS': avg_assists_high_scoring,
            '% Change in Assists': pct_change_assists,
            'Normal Average Rebounds': avg_rebounds_overall,
            'Rebounds with High PTS': avg_rebounds_high_scoring,
            '% Change in Rebounds': pct_change_rebounds,
            'Normal Average Points': avg_points_overall,
            'Points with High PTS': avg_points_high_scoring,
            '% Change in Points': pct_change_points
        })

    # Convert the list to a DataFrame
    player_avg_comparison = pd.DataFrame(player_data)

    # Display the DataFrame
    print(player_avg_comparison)

# Example usage:
player_full_name = 'Luka Doncic'  # Change this to the player of interest
team_full_name = 'Dallas Mavericks'  # Change this to the team of interest
season = '2023'  # Specify the season
points_threshold = 28  # Set
fetch_and_compare_player_stats(player_full_name, team_full_name, season, points_threshold)

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, commonteamroster
import pandas as pd

def fetch_and_compare_player_stats(player_full_name, team_full_name, season='2023', threshold=28, compare_stat='PTS'):
    # Validate compare_stat
    valid_stats = ['PTS', 'AST', 'REB', 'FG3M']
    if compare_stat not in valid_stats:
        print(f"Invalid compare_stat. Please use one of the following: {', '.join(valid_stats)}.")
        return
    
    # Get player ID and team ID
    player_info = [player for player in players.get_players() if player['full_name'].lower() == player_full_name.lower()]
    team_info = [team for team in teams.get_teams() if team['full_name'].lower() == team_full_name.lower()]
    if not player_info or not team_info:
        print("No player or team found with the given names.")
        return
    player_id = player_info[0]['id']
    team_id = team_info[0]['id']

    # Fetch roster and player game logs
    roster = commonteamroster.CommonTeamRoster(season=season, team_id=team_id)
    roster_df = roster.get_data_frames()[0]
    player_gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    player_df = player_gamelog.get_data_frames()[0]
    high_performance_games = player_df[player_df[compare_stat] > threshold]['Game_ID'].unique()

    # Initialize player data list
    player_data = []

    for index, row in roster_df.iterrows():
        player_id = row['PLAYER_ID']
        player_name = row['PLAYER']
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = gamelog.get_data_frames()[0]
        df_high_performance = df[df['Game_ID'].isin(high_performance_games)]
        avg_minutes_overall = df['MIN'].mean()
        if avg_minutes_overall < 15:
            continue        
        # Calculate averages and percentage changes
        stats = ['AST', 'REB', 'PTS', 'FG3M']
        avg_stats = {stat: df[stat].mean() for stat in stats}
        avg_high_performance_stats = {stat: df_high_performance[stat].mean() if not df_high_performance.empty else 0 for stat in stats}
        pct_changes = {f'% Change in {stat}': ((avg_high_performance_stats[stat] - avg_stats[stat]) / avg_stats[stat] * 100 if avg_stats[stat] else 0) for stat in stats}
        
        player_data.append({'Player Name': player_name, **pct_changes})

    player_avg_comparison = pd.DataFrame(player_data)

    # Display top 10 positive and negative percentage changes for each stat
    for stat in stats:
        pct_change_col = f'% Change in {stat}'
        print(f"Top 10 Positive Percentage Changes in {stat} ({compare_stat} > {threshold}):")
        print(player_avg_comparison.sort_values(by=pct_change_col, ascending=False).head(10)[['Player Name', pct_change_col]])
        print(f"\nTop 10 Negative Percentage Changes in {stat} ({compare_stat} > {threshold}):")
        print(player_avg_comparison.sort_values(by=pct_change_col, ascending=True).head(10)[['Player Name', pct_change_col]])
        print("\n" + "-"*50 + "\n")

# Example usage
fetch_and_compare_player_stats('Luka Doncic', 'Dallas Mavericks', '2023', 5, 'REB')


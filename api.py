from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, commonteamroster
import pandas as pd

def fetch_and_compare_player_stats_json(player_full_name, team_full_name, season='2023', threshold=28, compare_stat='PTS'):
    # Initialize response dictionary
    response = {"data": []}

    # Get player ID and team ID
    player_info = [player for player in players.get_players() if player['full_name'].lower() == player_full_name.lower()]
    team_info = [team for team in teams.get_teams() if team['full_name'].lower() == team_full_name.lower()]
    if not player_info or not team_info:
        return {"error": "No player or team found with the given names."}
    player_id = player_info[0]['id']
    team_id = team_info[0]['id']

    # Fetch roster and player game logs
    roster = commonteamroster.CommonTeamRoster(season=season, team_id=team_id)
    roster_df = roster.get_data_frames()[0]
    player_gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    player_df = player_gamelog.get_data_frames()[0]
    high_performance_games = player_df[player_df[compare_stat] > threshold]['Game_ID'].unique()

    # Process each player on the roster
    for index, row in roster_df.iterrows():
        player_id = row['PLAYER_ID']
        player_name = row['PLAYER']
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = gamelog.get_data_frames()[0]
        #traded check if player was traded
        if len(df['Game_ID']) < 10:
            continue       
        
        df_high_performance = df[df['Game_ID'].isin(high_performance_games)]
        avg_minutes_overall = df['MIN'].mean()
        if avg_minutes_overall < 12:
            continue        
        
        # Calculate averages and percentage changes
        stats = ['AST', 'REB', 'PTS', 'FG3M']
        avg_stats = {stat: df[stat].mean() for stat in stats}
        avg_high_performance_stats = {stat: df_high_performance[stat].mean() if not df_high_performance.empty else 0 for stat in stats}
        pct_changes = {f'% Change in {stat}': ((avg_high_performance_stats[stat] - avg_stats[stat]) / avg_stats[stat] * 100 if avg_stats[stat] else 0) for stat in stats}
        
        for stat in stats:
            avg_stats[stat] = round(avg_stats[stat], 2)
            avg_high_performance_stats[stat] = round(avg_high_performance_stats[stat], 2)
            pct_changes[f'% Change in {stat}'] = round(pct_changes[f'% Change in {stat}'], 2)
        
        # Append player data to response
        response["data"].append({
            'Player Name': player_name,
            'PTS Normal Average': avg_stats['PTS'],
            'AST Normal Average': avg_stats['AST'],
            'REB Normal Average': avg_stats['REB'],
            'FG3M Normal Average': avg_stats['FG3M'],
            'PTS with High PTS': avg_high_performance_stats['PTS'],
            'AST with High PTS': avg_high_performance_stats['AST'],
            'REB with High PTS': avg_high_performance_stats['REB'],
            'FG3M with High PTS': avg_high_performance_stats['FG3M'],
            '% Change in PTS': pct_changes['% Change in PTS'],
            '% Change in AST': pct_changes['% Change in AST'],
            '% Change in REB': pct_changes['% Change in REB'],
            '% Change in FG3M': pct_changes['% Change in FG3M'],            
        })

    return response

# Example usage (convert to JSON with Flask or another framework as needed):
#result = fetch_and_compare_player_stats_json('P.J. Washington', 'Dallas Mavericks', '2023', 5, 'REB')
#print(result)

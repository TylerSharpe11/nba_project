from flask import Flask, jsonify, render_template, request
from api import fetch_and_compare_player_stats_json
app = Flask(__name__)



@app.route('/api/compare_player_stats', methods=['GET'])
def api_compare_player_stats():
    player_full_name = request.args.get('player_full_name', default='Luka Doncic', type=str)
    team_full_name = request.args.get('team_full_name', default='Dallas Mavericks', type=str)
    season = request.args.get('season', default='2023', type=str)
    threshold = request.args.get('threshold', default=28, type=int)
    compare_stat = request.args.get('compare_stat', default='PTS', type=str)

    result = fetch_and_compare_player_stats_json(player_full_name, team_full_name, season, threshold, compare_stat)
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')  # Assuming you save the above HTML in a file named index.html within the 'templates' directory of your Flask app

if __name__ == '__main__':
    app.run(debug=True)

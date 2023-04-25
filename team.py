import requests
from PIL import Image
from io import BytesIO
from pathlib import Path

def download_logo(url, name):
    output_path = Path('static') / f'{name}.png'
    if not output_path.exists():
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        output_path.parent.mkdir(exist_ok=True, parents=True)
        img.save(output_path)
    return f'{name}.png'

class Team:
    def __init__(self, position, name, games, wins, draws, losses, goals, goal_difference, points, logoURL, lastGames):
        self.name = name
        self.points = points
        self.goals_scored = goals.split(':')[0]
        self.goals_against = goals.split(':')[1]
        self.games = games
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.goal_difference = goal_difference
        self.position = position
        self.lastGames = lastGames
        self.logoURL = download_logo(logoURL, name)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name + ' ' + self.points + ' ' + self.goals + ' ' + self.goalsAgainst + ' ' + self.wins + ' ' + self.draws + ' ' + self.losses + ' ' + self.place
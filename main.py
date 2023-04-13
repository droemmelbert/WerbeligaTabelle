import os
from datetime import date
from bs4 import BeautifulSoup
import requests
from team import Team
from flask import Flask, render_template

# variables
werbeligaURL = 'http://www.werbeliga.de/de/Spielplan,%20Tabelle%20&%20Torsch%C3%BCtzen' + \
    '?season=' + date.today().strftime('%y')
matchday_values = []
teams = []
last_five_gameday_matchups = []

# get current matchday value
url = werbeligaURL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# get all matchday values
for option in soup.find_all('select')[1].find_all('option'):
    matchday_values.append(option.get('value'))

# get current matchday value
for value in matchday_values:
    current_matchday_value = value
    currentMatchdayHTML = requests.get(
        url + '&match=' + current_matchday_value)
    soup = BeautifulSoup(currentMatchdayHTML.content, 'html.parser')
    # find first
    if soup.find_all('table')[0].find_all('tr')[1].find_all('td')[3].text.strip().split(' ')[0] != "-":
        break

# get last 5 games
for i in range(5):
    url = f"{werbeligaURL}&match={int(current_matchday_value) - i}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    if i == 0:
        # save current table
        current_table_html = soup.find_all('table')[1]
    # save current matchday matchups
    last_five_gameday_matchups.append(soup.find_all('table')[0])


def getLast5Games(teamName):
    last5 = []

    for table in last_five_gameday_matchups:
        rows = table.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) != 0:
                matchup = tds[2].text.strip()
                if matchup:
                    home_goals, away_goal = tds[3].text.strip().split(':')
                    home_goals, away_goal = int(home_goals), int(away_goal)
                    if matchup.split(':')[0].strip() == teamName:
                        if home_goals > away_goal:
                            last5.append('W')
                        elif home_goals < away_goal:
                            last5.append('L')
                        elif home_goals == away_goal:
                            last5.append('D')
                    elif matchup.split(':')[1].strip() == teamName:
                        if home_goals > away_goal:
                            last5.append('L')
                        elif home_goals < away_goal:
                            last5.append('W')
                        elif home_goals == away_goal:
                            last5.append('D')
    return last5


table = []
for row in current_table_html.find_all('tr'):
    rowStr = ''
    logoURL = ''
    for cell in row.find_all('td'):
        if len(cell.text.strip()) > 0:
            rowStr += cell.text.lstrip().rstrip() + ';'
        else:
            logoURL = row.find('img')['src']
    # add row without last semicolon
    if rowStr != '':
        table.append(rowStr + logoURL)


for line in table:
    data = line.split(';')
    name = data[1]
    last5 = getLast5Games(name)
    team = Team(*data, last5)
    teams.append(team)


# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', teams=teams)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

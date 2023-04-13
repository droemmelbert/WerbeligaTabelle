import os
from datetime import date
from bs4 import BeautifulSoup
import requests
from team import Team
from flask import Flask, render_template

# variables
werbeligaURL = 'http://www.werbeliga.de/de/Spielplan,%20Tabelle%20&%20Torsch%C3%BCtzen' + \
    '?season=' + date.today().strftime('%y')
current_matchday_value = ''
matchday_values = []
teams = []
last_five_gameday_matchups = []
current_table_html = ''

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
        print('\n\n### Found current matchday! ###')
        print('matchday_value: ' + current_matchday_value + '\n\n')
        break

# get last 5 games
for i in range(5):
    response = requests.get(werbeligaURL + '&match=' +
                            str(int(current_matchday_value) - i))
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
                if matchup and matchup.split(':')[0].strip() == teamName:
                    score = tds[3].text.strip()
                    if int(score.split(':')[0]) > int(score.split(':')[1]):
                        last5.append('W')
                    elif int(score.split(':')[0]) < int(score.split(':')[1]):
                        last5.append('L')
                    elif int(score.split(':')[0]) == int(score.split(':')[1]):
                        last5.append('D')
                elif matchup and matchup.split(':')[1].strip() == teamName:
                    score = tds[3].text.strip()
                    if int(score.split(':')[0]) > int(score.split(':')[1]):
                        last5.append('L')
                    elif int(score.split(':')[0]) < int(score.split(':')[1]):
                        last5.append('W')
                    elif int(score.split(':')[0]) == int(score.split(':')[1]):
                        last5.append('D')
    return last5


tableString = ''
for row in current_table_html.find_all('tr'):
    rowStr = ''
    logoURL = ''
    for cell in row.find_all('td'):
        if len(cell.text.strip()) > 0:
            rowStr += cell.text.lstrip().rstrip() + ';'
        else:
            logoURL = row.find('img')['src']
    # add row without last semicolon
    tableString += rowStr + logoURL + '\n'

tableString = tableString.rstrip()
tableString = tableString.splitlines()
tableString = [line for line in tableString if line]

for line in tableString:
    data = line.split(';')

    position = data[0]
    name = data[1]
    games = data[2]
    wins = data[3]
    draws = data[4]
    losses = data[5]
    goals = data[6].split(':')[0]
    goalsAgainst = data[6].split(':')[1]
    points = data[8]
    logoURL = data[9]

    last5 = getLast5Games(name)

    # new team
    team = Team(name, points, goals, goalsAgainst, wins,
                draws, losses, position, last5, logoURL)
    # add team to list
    teams.append(team)


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', teams=teams)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

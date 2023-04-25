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
matchday_html_list = [] # list of tuples (matchday, html)

# get current matchday value
url = werbeligaURL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# get all matchday values
for option in soup.find_all('select')[1].find_all('option'):
    matchday_values.append(option.get('value'))

# get html for all matchdays
for value in matchday_values:
    currentHTML = requests.get(url + '&match=' + value)
    soup = BeautifulSoup(currentHTML.content, 'html.parser')
    matchday_html_list.append((value,soup))

found_current_matchday = False
# get current matchday value
for item in matchday_html_list:
    if found_current_matchday == False:
        value = item[0]
        soup = item[1]
        current_matchday_value = value

        # find first matchup where result is not "-:-"
        rows = soup.find_all('table')[0].find_all('tr')
        for i in range(1, len(rows) - 1):
            game_score = rows[i].find_all('td')[3].text.strip() # either "- : -" or "1:1"
            if game_score != "- : -":
                found_current_matchday = True
                current_table_html = soup.find_all('table')[1]
                break
    else:
        break


def getLastGames(teamName):
    lastGames = []

    for matchday_value, html in matchday_html_list:
        # only get last 5 games
        if len(lastGames) < 5:
            rows = html.find_all('table')[0].find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) != 0:
                    matchup = tds[2].text.strip()
                    if matchup and tds[3].text.strip() != "- : -":
                        home_goals, away_goal = tds[3].text.strip().split(':')
                        home_goals, away_goal = int(home_goals), int(away_goal)
                        if matchup.split(':')[0].strip() == teamName:
                            if home_goals > away_goal:
                                lastGames.append('W')
                            elif home_goals < away_goal:
                                lastGames.append('L')
                            elif home_goals == away_goal:
                                lastGames.append('D')
                        elif matchup.split(':')[1].strip() == teamName:
                            if home_goals > away_goal:
                                lastGames.append('L')
                            elif home_goals < away_goal:
                                lastGames.append('W')
                            elif home_goals == away_goal:
                                lastGames.append('D')
        else:
            break
    return lastGames


team_info = []
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
        team_info.append(rowStr + logoURL)


for line in team_info:
    data = line.split(';')
    name = data[1]
    lastGames = getLastGames(name)
    team = Team(*data, lastGames)
    teams.append(team)


# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', teams=teams)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

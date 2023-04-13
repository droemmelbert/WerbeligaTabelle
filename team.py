# a class for a team

class Team:
    def __init__(self, name, points, goals, goalsAgainst, wins, draws, losses, position, last5, logoURL):
        self.name = name
        self.points = points
        self.goals = goals
        self.goalsAgainst = goalsAgainst
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.position = position
        self.last5 = last5
        self.logoURL = logoURL

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name + ' ' + self.points + ' ' + self.goals + ' ' + self.goalsAgainst + ' ' + self.wins + ' ' + self.draws + ' ' + self.losses + ' ' + self.place
    
    def getName(self):
        return self.name
    
    def getPoints(self):
        return self.points
    
    def getGoals(self):
        return self.goals
    
    def getGoalsAgainst(self):
        return self.goalsAgainst
    
    def getGoalDifference(self):
        return int(self.goals) - int(self.goalsAgainst)
    
    def getWins(self):
        return self.wins
    
    def getDraws(self):
        return self.draws
    
    def getLosses(self):
        return self.losses
    
    def getPlace(self):
        return self.place
    
    def getNumberOfGames(self):
        return int(self.wins) + int(self.draws) + int(self.losses)
    


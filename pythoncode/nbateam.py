from nba_py import team
import numpy as np
import config
import pandas as pd

class nbateam(object):
    
    def __init__(self, teamabbv, teamname, id, gamelogs):
        self.teamabbv = teamabbv
        self.name = teamname
        self.id = id
        pd.to_datetime(data['GAME_DATE'])
        self.gamelogs = gamelogs
        
    
    def record(self):
        wins = self.gamelogs['W'][0]
        loss = self.gamelogs['L'][0]
        diff = wins-loss
        
        return wins, loss, diff

    def recordrange(self):
        
        #wins = self.gamelogs['W'][0]
        #loss = self.gamelogs['L']
        #diff = wins-loss
        
        return wins, loss, diff
        
        
#gamelogs = team.TeamGameLogs('1610612737', season='2016-17').info()[['GAME_DATE','MATCHUP','WL','W', 'L', 'W_PCT']]


#t = []
#for k,v in team.TEAMS.iteritems():
#    igl = team.TeamGameLogs(v.id, season=SEASON).info()[['GAME_DATE','MATCHUP','WL','W', 'L', 'W_PCT']]
#    t.append(nbateam(k, v.name, v.id, igl))
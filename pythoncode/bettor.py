from nba_py import team
import pytz
import datetime as dt
import pandas as pd
import time

import config

schedule_file = config.SCHEDULE_FILE
SEASON = config.SEASON
START_DATE = config.START_DATE
tz = pytz.timezone('EST')
today = dt.datetime.now(tz)
STR_TODAY = '%i/%i/%i' % (today.month, today.day, today.year)
END_DATE = '%i-%i-%i' % (today.year, today.month, today.day)
idx = pd.date_range(START_DATE, END_DATE)

# Upload the current schedule and convert date to timestamp
nba_sched = pd.read_csv(schedule_file, index_col=0)
nba_sched.index = pd.to_datetime(nba_sched.index)
teamids = {value['name']:{'id': value['id'],'abbr':value['abbr']} for key,value in team.TEAMS.iteritems()}

class Bettor():
    """Class for a bettor or person that has an array of Team objects and other
       useful utilities"""
    def __init__(self, name, order, teams):
        print name
        self.name = name
        self.order = order
        self.teams = teams
        if order == 0:
            self.picks = [1, 6, 7, 12, 13, 18, 19, 24, 25, 30]
        elif order == 1:
            self.picks = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29]
        else:
            self.pickes = [3, 4, 9, 10, 15, 16, 21, 22, 27, 28]
        self.team_objs = self.all_teams()

    # Creates dictionary of Team objects where the key is the teamname
    def all_teams(self):
        team_obj_dict = {}
        for teamname in self.teams:
            print teamname
            team_obj_dict[teamname] = Team(teamname)
            time.sleep(0.5)
        return team_obj_dict

    # Calculate how many games left in a season that a Bettor plays their own team (int)
    def dup_remaining_games(self):
        # Get today's date
        today = dt.datetime.strptime(STR_TODAY, '%m/%d/%Y').isoformat()

        # Remove all of the games that have already been played. Assumes today's
        # games haven't been played yet.
        nba_sched_remain = nba_sched.loc[nba_sched.index >= today]
        nba_sched_remain['Home'] = nba_sched_remain['Home/Neutral'].str.split().str[-1]
        nba_sched_remain['Visitor'] = nba_sched_remain['Visitor/Neutral'].str.split().str[-1]
        bettor_teams = list(self.teams)
        if 'Trail Blazers' in bettor_teams:
            bettor_teams.append('Blazers')
        if 'Sixers' in bettor_teams:
            bettor_teams.append('76ers')
        dups_games = nba_sched_remain[(nba_sched_remain['Home'].isin(bettor_teams)) &
                                      (nba_sched_remain['Visitor'].isin(bettor_teams)) ]
        return dups_games.shape[0]

    # Returns all current wins (int)
    def all_wins(self):
        return sum([self.team_objs[team].wins() for team in self.team_objs])

    # Returns all current losses (int)
    def all_losses(self):
        return sum([self.team_objs[team].losses() for team in self.team_objs])

    # Returns all remaining games (int)
    def all_remaining(self):
        return len(self.teams)*82 - self.all_wins() - self.all_losses()

class Team():
    """Class for a team that contains gamelog information and other
       useful utilities"""
    def __init__(self, teamname):
        self.name = teamname
        self.id = teamids[self.name]['id']
        self.abbr = teamids[self.name]['abbr']
        self.gamelog = self.gamelog_proc()

    # Processes gamelog with correct parameters
    def gamelog_proc(self):
        gamelog = team.TeamGameLogs(self.id, season=SEASON).info()[['GAME_DATE', 'WL']]
        gamelog['GAME_DATE'] = pd.to_datetime(gamelog['GAME_DATE'])
        gamelog = gamelog[gamelog['GAME_DATE'] < today]
        #gamelog = gamelog[gamelog['GAME_DATE'] < (today - dt.timedelta(days=2))]

        return gamelog

    # Calculate the last 10 games W-L (str)
    def last10(self):
        last10gameswins = sum(self.gamelog['WL'][:10].str.count('W'))
        last10gameslosses = sum(self.gamelog['WL'][:10].str.count('L'))
        return '%i-%i' % (last10gameswins, last10gameslosses)

    # The populated full calendar DF that fills in missing dates with a dash
    def full_calendar_gamelog(self):
        df = self.gamelog.set_index(['GAME_DATE']).reindex(idx, fill_value='-').truncate(after=STR_TODAY)
        df.fillna(value='-', inplace=True)
        return df

    # The running sum of wins for full calendar (DF)
    def wins_calendar(self):
        df = self.full_calendar_gamelog()
        return df['WL'].cumsum().str.count('W')

    # The running sum of losses for full calendar (DF)
    def losses_calendar(self):
        df = self.full_calendar_gamelog()
        return df['WL'].cumsum().str.count('L')

    # The running sum of wins-losses for full calendar (DF)
    def diff_calendar(self):
        return self.wins_calendar() - self.losses_calendar()

    # Team's current wins (int)
    def wins(self):
        return self.wins_calendar()[-1]

    # Team's current losses (int)
    def losses(self):
        return self.losses_calendar()[-1]

    # Team's number of remaining games in the season (int)
    def remaining(self):
        return 82-self.wins() - self.losses()

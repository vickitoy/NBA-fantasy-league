#!/Users/ttshimiz/anaconda/bin/python

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from nba_py import team
import time
import pytz

SEASON = '2017-18'
START_DATE = '2017-10-16'
tz = pytz.timezone('EST')
today = dt.datetime.now(tz)
STR_TODAY = '%i/%i/%i' % (today.month, today.day, today.year)
END_DATE = '%i-%i-%i' % (today.year, today.month, today.day)


def calc_current_wins(person_dict):

    idx = pd.date_range(START_DATE, END_DATE)
    for person in person_dict:
        print person
        for order,bteam in enumerate(person_dict[person]):
            print bteam['teamname']
            ts = team.TeamGameLogs(bteam['id'], season=SEASON).info()[['GAME_DATE', 'WL']] 
            
            ts['GAME_DATE'] = pd.to_datetime(ts['GAME_DATE'])
            ts = ts.set_index(['GAME_DATE']).reindex(idx, fill_value='-').truncate(after=STR_TODAY)
            ts.fillna(value='-', inplace=True)
            ts['losses'] = ts['WL'].cumsum().str.count('L')
            ts['wins'] = ts['WL'].cumsum().str.count('W') 
            ts['remaining'] = 82-ts['wins']-ts['losses'] 
            ts = ts.drop('WL', axis=1)
            person_dict[person][order]['df'] = ts         
            time.sleep(1)

    return person_dict
   
def calc_duplicate_remaining_games(team_bettor, pick_order):

    bettor_remaining = {person: 0 for person in pick_order}

    # Upload the current schedule and convert date to timestamp
    nba_sched = pd.read_csv('2017_schedule.txt', index_col=0)
    nba_sched.index = pd.to_datetime(nba_sched.index)
    
    # Get today's date
    today = dt.datetime.strptime(STR_TODAY, '%m/%d/%Y').isoformat()   
    
    # Remove all of the games that have already been played. Assumes today's
    # games haven't been played yet.
    nba_sched_remain = nba_sched.loc[nba_sched.index >= today]

    # Count remaining games where bettor plays themselves
    for game in np.unique(nba_sched_remain.index):
    
        home_teams = nba_sched_remain.loc[game, 'Home/Neutral']
        away_teams = nba_sched_remain.loc[game, 'Visitor/Neutral']
        
        if isinstance(home_teams, str):
            home_teams = [home_teams]
            away_teams = [away_teams]
        
        for i in range(len(home_teams)):
            ht = home_teams[i].split()[-1]
            at = away_teams[i].split()[-1]  

            ht = ht.replace('Blazers', 'Trail Blazers')
            at = at.replace('Blazers', 'Trail Blazers')
            ht = ht.replace('76ers', 'Sixers')
            at = at.replace('76ers', 'Sixers')
            
            if team_bettor[ht] == team_bettor[at]:
                bettor_remaining[team_bettor[ht]] += 1

    return bettor_remaining
    
def create_graph_data(person_dict,dup_remaining_games):

    sched_dates = pd.date_range(start=START_DATE, end=STR_TODAY)
        
    df_bettor = pd.DataFrame()
    
    bettor_summary = {}
    for bettor in person_dict:
        bettor_summary[bettor] = np.array([0,0,0])
        for i,iteam in enumerate(person_dict[bettor]):
            if i == 0:
                df = iteam['df'].copy()
            else:
                df += iteam['df']
                
            bettor_summary[bettor] += (iteam['df']['wins'].iloc[-1], iteam['df']['losses'].iloc[-1],iteam['df']['remaining'].iloc[-1])
        
        df_bettor[bettor+'_wins'] = df['wins']
        df_bettor[bettor+'_losses'] = df['losses']
        df_bettor[bettor+'_winperc'] = df_bettor[bettor+'_wins']/(df_bettor[bettor+'_wins']+df_bettor[bettor+'_losses'])
                
        df_bettor[bettor+'_diff'] = df_bettor[bettor+'_wins'] - df_bettor[bettor+'_losses']
        bettor_summary[bettor][2] -= dup_remaining_games[bettor]
    
    return df_bettor, bettor_summary


def plot_graph(wins_losses, pick_order): 
     # Plot winning percentage as a function of time
    sn.set(color_codes=True)
    fig = plt.figure(figsize=(6.5, 3))
    ax = fig.add_subplot(111)
    ax = wins_losses.plot(y=[pick_order[0]+'_diff', pick_order[1]+'_diff', pick_order[2]+'_diff'], ax=ax)
    ax.legend(pick_order, loc='lower left')    
    ax.set_ylabel('Wins - Losses', fontsize=12)
    fig.savefig('win_percent.png', bbox_inches='tight')
    plt.close(fig)
    
    return 
    
def make_html(current_totals, order, team_pickorder):

    with open('../template.html', 'r') as ftemp:
        temp = ftemp.read()
    
    current_winner = max([(v[0],k) for k,v in bettor_summary.iteritems()])[1]
    
    html_string = [STR_TODAY, current_winner.title()]
    
    for bettor in order:
        html_string += [bettor.title(),bettor.title()] + list(current_totals[bettor])

    team_pickorder = [bettor.title() for bettor in team_pickorder]

    html_string += team_pickorder
              
    print html_string
    updated = temp % tuple(html_string)
                      
    with open('../bet.html', 'w') as findex:
        findex.write(updated)
        
    return
    
def make_bettor_html(current_totals, person_dict):

    for person in person_dict:
        with open('../template_bettor.html', 'r') as ftemp:
            temp = ftemp.read()   

        team_list = []
        for iteam in person_dict[person]:
            team_list += [iteam['teamname'],iteam['df']['wins'].iloc[-1], iteam['df']['losses'].iloc[-1],iteam['df']['remaining'].iloc[-1]]

        html_string = [person.title()] + list(current_totals[person]) + team_list
         
        print html_string
        updated = temp % tuple(html_string)
                      
        with open('../'+person.title()+'.html', 'w') as findex:
            findex.write(updated)
     
    return

if __name__ == '__main__':
    
    pick_order = np.loadtxt('pickorder.txt', dtype=str, delimiter='\t')
    teamids = {value['name']:value['id'] for key,value in team.TEAMS.iteritems()}
    
    person_dict = {}
    for bettor in pick_order:
        bettor = bettor.lower()
        bettor_teams = np.loadtxt(bettor+'_teams17-18.txt', dtype=str, delimiter='\t')
        
        person_dict[bettor] = [{'teamname':iteam, 'id':teamids[iteam]} for iteam in bettor_teams]
    
    team_bettor = {iteam['teamname']:ibettor for ibettor in person_dict for iteam in person_dict[ibettor]}
    
    # Calculate total wins and losses to date
    person_dict = calc_current_wins(person_dict)
    
    # Calculate maximum remaining wins left
    dup_remaining_games = calc_duplicate_remaining_games(team_bettor, pick_order)

    # Calculate each W-L record as a function of time for graph
    wins_losses, bettor_summary = create_graph_data(person_dict, dup_remaining_games)
        
    # Plot the graph and save as image
    plot_graph(wins_losses,list(pick_order))

    team_pickorder = list(pick_order) + [person_dict[bettor][i]['teamname'] for i in range(10) for bettor in pick_order]
    
    # Generate updated HTML file
    make_html(bettor_summary, pick_order, team_pickorder)
    make_bettor_html(bettor_summary,person_dict)

#!/Users/ttshimiz/anaconda/bin/python

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from nba_py import team
import time

SEASON = '2016-17'
START_DATE = '10/25/2016'
today = dt.datetime.now() - dt.timedelta(hours=6)
TODAY = today.date()
#STR_TODAY = '%i/%i/%i' % (today.month, today.day, today.year)
STR_TODAY = '10/26/2016'

def calc_current_wins(person_dict):

    win_loss = []
    order = []
    for person in person_dict:
        iwin_loss = [0,0]
        print person
        for bteam in person_dict[person]:
            print bteam
            ts = team.TeamSummary(bteam[2], season=SEASON).info()
            
            iwin_loss[0] += ts['W'][0]
            iwin_loss[1] += ts['L'][0]
            time.sleep(1)
        win_loss.append(iwin_loss)
        order.append(person)
    return win_loss, order
     
   
def calc_remaining_wins(team_bettor, bettor_remaining):

    # Upload the current schedule
    nba_sched = pd.read_csv('2016_schedule.txt', index_col=0)
    
    # Convert the date to a Timestamp
    nba_sched.index = pd.to_datetime(nba_sched.index)
    
    # Get today's date
    today = dt.date.today().isoformat()
    
    # Remove all of the games that have already been played. Right now assumes today's
    # games haven't been played yet.
    nba_sched_remain = nba_sched.loc[nba_sched.index >= today]
    
    # Loop through the remaining games. Assume exactly 1 win for every game a person has
    # a team playing in. If they have 2 teams playing each other, that only counts a 1 win
    
    for game in np.unique(nba_sched_remain.index):
    
        home_teams = nba_sched_remain.loc[game, 'Home/Neutral']
        away_teams = nba_sched_remain.loc[game, 'Visitor/Neutral']

        
        for i in range(len(home_teams)):
            ht = home_teams[i].split()[-1]
            at = away_teams[i].split()[-1]

            if ht == 'Blazers':
                ht = 'Trail Blazers'
            if at == 'Blazers':
                at = 'Trail Blazers'
                
            if ht == '76ers':
                ht = 'Sixers'
            if at == '76ers':
                at = 'Sixers'

            if team_bettor[ht] == team_bettor[at]:
                bettor_remaining[team_bettor[ht]] += 1
            else:
                bettor_remaining[team_bettor[ht]] += 1
                bettor_remaining[team_bettor[at]] += 1
    
    return bettor_remaining
    
def create_graph_data(person_dict):

    sched_dates = pd.date_range(start=START_DATE, end=STR_TODAY)
    
    column_names = [i+'_win' for i in person_dict.keys()] + [i+'_losses' for i in person_dict.keys()]
    
    df = pd.DataFrame(index=sched_dates, columns=column_names)
    
    for bettor in person_dict:
    
        for tup in person_dict[bettor]:
            id = tup[2]
            data = team.TeamGameLogs(id, season=SEASON).info()[['GAME_DATE', 'WL']]
            df[bettor+'_wins'] = 0
            df[bettor+'_losses'] = 0
            if not data.empty:
                data.index = pd.to_datetime(data['GAME_DATE'])
                data = data.sort_index()
                for d in df.index:
                    df.loc[d, bettor+'_wins'] = df.loc[d, bettor+'_wins']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'W')
                    df.loc[d, bettor+'_losses'] = df.loc[d, bettor+'_losses']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'L')
            time.sleep(1)
        df[bettor+'_winperc'] = df[bettor+'_wins']/(df[bettor+'_wins']+df[bettor+'_losses'])
                
        df.fillna(value=0, inplace=True)
        df[bettor+'_diff'] = df[bettor+'_wins'] - df[bettor+'_losses']
    
    return df       
 

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
    
    current_totals = current_totals.sort_values('wins', ascending=False)
    current_winner = current_totals.index[0] 
    
    html_string = [STR_TODAY, current_winner]
    
    for bettor in order:
        html_string += [bettor,bettor, current_totals.loc[bettor]['wins'],
                        current_totals.loc[bettor]['losses'],
                        current_totals.loc[bettor]['remaining']]

    html_string += team_pickorder
              
    print html_string
    updated = temp % tuple(html_string)
                      
    with open('../index.html', 'w') as findex:
        findex.write(updated)
        
    return
    
def make_bettor_html(current_totals, person_dict):
    
    current_totals = current_totals.sort_values('wins', ascending=False)
    current_winner = current_totals.index[0] 
    
    for person in person_dict:
        with open('../template_bettor.html', 'r') as ftemp:
            temp = ftemp.read()   

        bettor_records = []
        for bteam in person_dict[person]:
            t = team.TeamSummary(bteam[2], season=SEASON).info()
            bettor_records += [t['TEAM_NAME'][0], t['W'][0], t['L'][0], 82-t['W'][0]-t['L'][0]]
            time.sleep(1)

        html_string = [person,
                      current_totals.loc[person]['wins'],
                      current_totals.loc[person]['losses'],
                      current_totals.loc[person]['remaining']] + bettor_records
    
                      
        print html_string
        updated = temp % tuple(html_string)
                      
        with open('../'+person+'.html', 'w') as findex:
            findex.write(updated)
     
    return


if __name__ == '__main__':
    
    pick_order = np.loadtxt('pickorder.txt', dtype=str, delimiter='\t')
    teamids = [(key,value['name'],value['id']) for key,value in team.TEAMS.iteritems()]
    
    person_dict = {}
    team_bettor = {}
    team_pickorder = []
    remaining_games = {}
    for bettor in pick_order:
        bettor = bettor.lower()
        bettor_teams = np.loadtxt(bettor+'_teams16-17.txt', dtype=str, delimiter='\t')
        team_pickorder.append(list(bettor_teams))
        person_dict[bettor] = [z for z in teamids if z[1].startswith(tuple(bettor_teams))]
        iteam_bettor = {iteam:bettor for iteam in bettor_teams}
        team_bettor.update(iteam_bettor)
        remaining_games[bettor] = 0

    team_pickorder = [val for pair in zip(team_pickorder[0],team_pickorder[1],team_pickorder[2]) for val in pair] 
    
    team_pickorder = list(pick_order) +team_pickorder
    
    # Calculate total wins and losses to date
    records, order = calc_current_wins(person_dict)
    
    # Calculate maximum remaining wins left
    remaining_games = calc_remaining_wins(team_bettor, remaining_games)
    
    # Calculate each W-L record as a function of time for graph
    wins_losses = create_graph_data(person_dict)
    
    # Plot the graph and save as image
    plot_graph(wins_losses,list(pick_order))
  
    # Generate updated HTML file
    current_totals = pd.DataFrame(index=list(pick_order), columns=['wins', 'losses', 'remaining'])
    for i, bettor in enumerate(order):
        current_totals.loc[bettor] = records[i] + [remaining_games[bettor]]

    make_html(current_totals, order, team_pickorder)
    make_bettor_html(current_totals,person_dict)

#!/Users/ttshimiz/anaconda/bin/python

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
from nba_py import team

SEASON = '2016-17'
START_DATE = '10/25/2016'
today = dt.datetime.now() - dt.timedelta(hours=6)
TODAY = today.date()
STR_TODAY = '%i/%i/%i' % (today.month, today.day, today.year)

def calc_current_wins(vicki_ids, johnny_ids, taro_ids):

    vwins = 0; vloss = 0
    jwins = 0; jloss = 0
    twins = 0; tloss = 0
    
    for id in vicki_ids:
        
        ts = team.TeamSummary(id, season=SEASON).info()
        vwins += ts['W'][0]
        vloss += ts['L'][0]
    
    for id in johnny_ids:
        
        ts = team.TeamSummary(id, season=SEASON).info()
        jwins += ts['W'][0]
        jloss += ts['L'][0]
        
    for id in taro_ids:
        
        ts = team.TeamSummary(id, season=SEASON).info()
        twins += ts['W'][0]
        tloss += ts['L'][0]
        
    return [[vwins, vloss], [jwins, jloss], [twins, tloss]]
     
   
def calc_remaining_wins(vicki, johnny, taro):

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
    vwins_remain = 0
    jwins_remain = 0
    twins_remain = 0
    vwins_not_guaranteed = 0
    jwins_not_guaranteed = 0
    twins_not_guaranteed = 0
    
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
                
            if (any(ht == np.array(vicki)) | any(at == np.array(vicki))):
                vwins_remain += 1
                if not (any(ht == np.array(vicki)) & any(at == np.array(vicki))):
                    vwins_not_guaranteed += 1
        
            if (any(ht == np.array(johnny)) | any(at == np.array(johnny))):
                jwins_remain += 1
                if not (any(ht == np.array(johnny)) & any(at == np.array(johnny))):
                    jwins_not_guaranteed += 1

            if (any(ht == np.array(taro)) | any(at == np.array(taro))):
                twins_remain += 1
                if not (any(ht == np.array(taro)) & any(at == np.array(taro))):
                    twins_not_guaranteed += 1
    
    return vwins_remain, jwins_remain, twins_remain
    
def create_graph_data(vids, jids, tids):

    sched_dates = pd.date_range(start=START_DATE, end=STR_TODAY)
    
    df = pd.DataFrame(index=sched_dates, columns=['vicki_wins', 'vicki_losses', 
                                                  'johnny_wins', 'johnny_losses',
                                                  'taro_wins', 'taro_losses'])
    df['vicki_wins'] = 0
    df['johnny_wins'] = 0
    df['taro_wins'] = 0
    df['vicki_losses'] = 0
    df['johnny_losses'] = 0
    df['taro_losses'] = 0
    
    for id in vids:
        data = team.TeamGameLogs(id, season=SEASON).info()[['GAME_DATE', 'WL']]
        print data
        if not data.empty:
            data.index = pd.to_datetime(data['GAME_DATE'])
            data = data.sort_index()
            for d in df.index:
                df.loc[d, 'vicki_wins'] = df.loc[d, 'vicki_wins']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'W')
                df.loc[d, 'vicki_losses'] = df.loc[d, 'vicki_losses']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'L')

    for id in jids:
        data = team.TeamGameLogs(id, season=SEASON).info()[['GAME_DATE', 'WL']]
        if not data.empty:
            data.index = pd.to_datetime(data['GAME_DATE'])
            data = data.sort_index()
            for d in df.index:
                df.loc[d, 'johnny_wins'] = df.loc[d, 'johnny_wins']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'W')
                df.loc[d, 'johnny_losses'] = df.loc[d, 'johnny_losses']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'L')

    for id in tids:
        data = team.TeamGameLogs(id, season=SEASON).info()[['GAME_DATE', 'WL']]
        if not data.empty:
            data.index = pd.to_datetime(data['GAME_DATE'])
            data = data.sort_index()
            for d in df.index:
                df.loc[d, 'taro_wins'] = df.loc[d, 'taro_wins']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'W')
                df.loc[d, 'taro_losses'] = df.loc[d, 'taro_losses']+np.sum(data.loc[df.index[0]:d, 'WL'] == 'L')
                
    df['taro_winperc'] = df['taro_wins']/(df['taro_wins']+df['taro_losses'])
    df['vicki_winperc'] = df['vicki_wins']/(df['vicki_wins']+df['vicki_losses'])
    df['johnny_winperc'] = df['johnny_wins']/(df['johnny_wins']+df['johnny_losses'])
    df.fillna(value=0, inplace=True)
    
    df['taro_diff'] = df['taro_wins'] - df['taro_losses']
    df['vicki_diff'] = df['vicki_wins'] - df['vicki_losses']
    df['johnny_diff'] = df['johnny_wins'] - df['johnny_losses']
    
    return df       
 

def plot_graph(wins_losses): 
     # Plot winning percentage as a function of time
    sn.set(color_codes=True)
    fig = plt.figure(figsize=(6.5, 3))
    ax = fig.add_subplot(111)
    #ax = wins_losses.plot(y=['vicki_winperc', 'taro_winperc', 'johnny_winperc'], ax=ax)
    ax = wins_losses.plot(y=['vicki_diff', 'taro_diff', 'johnny_diff'], ax=ax)
    ax.legend(['Vicki', 'Taro', 'Johnny'])    
    #ax.set_xlabel('Date', fontsize=12)
    #ax.set_ylabel('Winning Percentage', fontsize=12)
    ax.set_ylabel('Wins - Losses', fontsize=12)
    fig.savefig('win_percent.png', bbox_inches='tight')
    plt.close(fig)
    
    return 
    
def make_html(current_totals):

    with open('../template.html', 'r') as ftemp:
        temp = ftemp.read()
    
    current_totals = current_totals.sort_values('wins', ascending=False)
    current_winner = current_totals.index[0]    
    updated = temp % (STR_TODAY, current_winner,
                      current_totals.loc['Johnny']['wins'], current_totals.loc['Johnny']['losses'], current_totals.loc['Johnny']['remaining'],
                      current_totals.loc['Taro']['wins'], current_totals.loc['Taro']['losses'], current_totals.loc['Taro']['remaining'],
                      current_totals.loc['Vicki']['wins'], current_totals.loc['Vicki']['losses'], current_totals.loc['Vicki']['remaining'])
                      
    with open('../index.html', 'w') as findex:
        findex.write(updated)
        
    return


if __name__ == '__main__':
    
    # Upload each of our teams from separate text files
    vicki = np.loadtxt('vicki_teams16-17.txt', dtype=str, delimiter='\t')
    johnny = np.loadtxt('johnny_teams16-17.txt', dtype=str)
    taro = np.loadtxt('taro_teams16-17.txt', dtype=str, delimiter='\t')
    
    vicki_ids = []
    johnny_ids = []
    taro_ids = []
    
    # Get the IDs for each team
    for t in team.TEAMS.keys():
        
        tm = team.TEAMS[t]
        
        if np.any(vicki == tm['name']):
            vicki_ids.append(tm['id'])
        elif np.any(johnny == tm['name']):
            johnny_ids.append(tm['id'])
        elif np.any(taro == tm['name']):
            taro_ids.append(tm['id'])
        else:
            raise ValueError('{0} not on any team!'.format(tm['name']))
    
    # Calculate total wins and losses to date
    vrecord, jrecord, trecord = calc_current_wins(vicki_ids, johnny_ids, taro_ids)
    vwins = vrecord[0]; vloss = vrecord[1]
    jwins = jrecord[0]; jloss = jrecord[1]
    twins = trecord[0]; tloss = trecord[1]
    
    # Calculate maximum remaining wins left
    vwins_remain, jwins_remain, twins_remain = calc_remaining_wins(vicki, johnny, taro)
    
    # Calculate each W-L record as a function of time for graph
    wins_losses = create_graph_data(vicki_ids, johnny_ids, taro_ids)
    
    # Plot the graph and save as image
    plot_graph(wins_losses)
    
    # Generate updated HTML file
    current_totals = pd.DataFrame(index=['Vicki', 'Johnny', 'Taro'], columns=['wins', 'losses', 'remaining'])
    current_totals.loc['Vicki'] = [vwins, vloss, vwins_remain]
    current_totals.loc['Johnny'] = [jwins, jloss, jwins_remain]
    current_totals.loc['Taro'] = [twins, tloss, twins_remain]
    make_html(current_totals)

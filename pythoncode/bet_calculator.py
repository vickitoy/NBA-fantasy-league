#!/bin/python

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sn
import time
import pytz
import os
import shutil  

import config
from bettor import Bettor, Team

bet_file_postfix = config.BET_FILE_POSTFIX
schedule_file = config.SCHEDULE_FILE
SEASON = config.SEASON
START_DATE = config.START_DATE
tz = pytz.timezone('EST')
today = dt.datetime.now(tz)
STR_TODAY = '%i/%i/%i' % (today.month, today.day, today.year)

def todays_games(person_list):
    team_bettor_dict = {team: person_obj.name for person_obj in person_list for team in person_obj.team_objs.keys()}
    team_bettor_dict['Blazers'] = team_bettor_dict['Trail Blazers']
    team_bettor_dict['76ers'] = team_bettor_dict['Sixers']
    # Upload the current schedule and convert date to timestamp
    nba_sched = pd.read_csv(schedule_file, index_col=0)
    nba_sched.index = pd.to_datetime(nba_sched.index)

    # Get today's date
    today = dt.datetime.strptime(STR_TODAY, '%m/%d/%Y').isoformat()

    # Grabs todays games
    nba_sched_today = nba_sched.loc[nba_sched.index == today]
    nba_sched_today['HomeShort'] = nba_sched_today['Home/Neutral'].str.split().str[-1]
    nba_sched_today['VisitorShort'] = nba_sched_today['Visitor/Neutral'].str.split().str[-1]

    games = ''
    for index, row in nba_sched_today.iterrows():
        ht = row['HomeShort']
        at = row['VisitorShort']

        games += html_table_add_row([ht + ' ('+team_bettor_dict[ht].title()+')',at + ' ('+team_bettor_dict[at].title()+')'])

    return games


def determine_current_pick_order(person_list):
    """
    Assign a new pick number for every team based on current win percentage.
    """
    win_pct = pd.DataFrame(columns=['win pct'])
    for person_obj in person_list:

        for team in person_obj.teams:

            team_obj = person_obj.team_objs[team]
            s = pd.Series(name=team_obj.name, data={'win pct': float(team_obj.wins())/float(team_obj.wins()+team_obj.losses())})
            win_pct = win_pct.append(s)

    win_pct.sort_values('win pct', inplace=True, ascending=False)
    win_pct['new pickno'] = range(1, 31)

    for person_obj in person_list:

        for team in person_obj.teams:

            person_obj.team_objs[team].new_pickno = win_pct.loc[team, 'new pickno']

    return


def plot_graph_all(person_list):
    """Creates bettor 30-day and all season Wins-Losses graphs and creates
       graphs that displays the Wins-Losses for a bettor's set of teams"""

    # Create a DF with every calendar day with the summed Wins-Losses for each bettor
    summed_diff_calendar_list = [reduce((lambda x, y: x+y),
        [person_obj.team_objs[team].diff_calendar() for team in person_obj.teams])
        for person_obj in person_list ]

     # Plot Wins-Losses as a function of time for last 30 days
    sn.set(color_codes=True)
    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(111)
    for i in range(len(person_list)):
        summed_diff_calendar_list[i][today - dt.timedelta(days=30):today].plot()
    ax.legend(pick_order, loc='lower left')
    ax.set_ylabel('Wins - Losses', fontsize=12)
    fig.savefig('../images/win_percent_recent.png', bbox_inches='tight')
    plt.close(fig)

     # Plot Wins-Losses as a function of time for season so far
    sn.set(color_codes=True)
    fig = plt.figure(figsize=(6.5, 3))
    ax = fig.add_subplot(111)
    for i in range(len(person_list)):
        summed_diff_calendar_list[i].plot()
    ax.legend([person_obj.name for person_obj in person_list], loc='lower left')
    ax.set_ylabel('Wins - Losses', fontsize=12)
    fig.savefig('../images/win_percent_all.png', bbox_inches='tight')
    plt.close(fig)

    # Plot Wins-Losses for each bettor by team
    sn.set_palette(sn.color_palette("hls", 10))
    for order, person_obj in enumerate(person_list):
        # DF with every calendar day for each of the Bettor's teams
        team_diff_calendar_list = [person_obj.team_objs[team].diff_calendar() for team in person_obj.teams]
        fig = plt.figure(figsize=(10, 6.5))
        ax = fig.add_subplot(111)
        for iteam in person_obj.teams:
            person_obj.team_objs[iteam].diff_calendar().plot(label=iteam, ax=ax)
        ax.set_ylabel('Wins - Losses', fontsize=12)
        ax.legend()
        fig.savefig('../images/'+str(order+1)+'_teams.png', bbox_inches='tight')
        plt.close(fig)

    return

def make_html(person_list):
    """Populate main HTML page that summarizes bettors status and tonight's matchups"""
    with open('../template.html', 'r') as ftemp:
        temp = ftemp.read()

    # Person with the most wins
    current_winner = max([(person_obj.all_wins(), person_obj.name) for person_obj in person_list])[1]
    
    shutil.copyfile('../images/current_winner_'+current_winner+'.jpg', '../images/current_winner.jpg')  

    # Use html_string to dump information into HTML page
    html_string = [current_winner, STR_TODAY, current_winner.title()]

    # Every bettor's quick stats
    wins, losses, remaining, draft_value = [],[],[],[]
    for person_obj in person_list:
        html_string += [person_obj.name.title()]
        wins.append(person_obj.all_wins())
        losses.append(person_obj.all_losses())
        remaining.append(person_obj.all_remaining()-person_obj.dup_remaining_games())
        draft_value.append(person_obj.all_draft_value())

    html_string += wins + losses + remaining + draft_value

    # Order of teams that were picked by a bettor
    # -> Bettor 1 pick 1, Bettor 2 pick 1, Bettor 3 pick 1, Bettor 1 pick 2, etc
    team_pickorder = [person_obj.name.title() for person_obj in person_list] + [person_obj.teams[i]+' ('+str(person_obj.team_objs[person_obj.teams[i]].new_pickno)+')' for i in range(10) for person_obj in person_list]

    html_string += team_pickorder

    # Today's games (by team and bettor)
    html_string += [todays_games(person_list)]
    updated = temp % tuple(html_string)

    with open('../bet.html', 'w') as findex:
        findex.write(updated)

    return

def make_bettor_html(person_list):
    """Make individual bettor page information that breaks down a bettor's teams"""
    with open('../template_bettor.html', 'r') as ftemp:
        temp = ftemp.read()
    html_string = [person_obj.name.title() for person_obj in person_list]
    for person_obj in person_list:

        team_list = ''
        # Summary of team information for a bettor
        for teamname in person_obj.teams:
            team_obj = person_obj.team_objs[teamname]
            team_list += html_table_add_row([teamname,
                                             team_obj.wins(),
                                             team_obj.losses(),
                                             team_obj.remaining(),
                                             team_obj.last10()], align="center")

        html_string += [person_obj.name.title(), person_obj.all_wins(), person_obj.all_losses(),
                        person_obj.all_remaining()-person_obj.dup_remaining_games(),team_list]

    updated = temp % tuple(html_string)

    with open('../bettors.html', 'w') as findex:
        findex.write(updated)

    return

def html_table_add_row(element_list, align="left"):
    """Simple html table row"""
    connector = '    </td><td align="'+align+'">'
    table_str = '  <tr><td align="'+align+'">'
    table_str += connector.join(str(e) for e in element_list)
    table_str += '  </td></tr>'
    return table_str

if __name__ == '__main__':

    # Read in bettor pick order
    pick_order = np.loadtxt('pickorder.txt', dtype=str, delimiter='\t')

    # Create list of Bettor objects and initialize them
    person_list = []
    for order, bettor in enumerate(pick_order):
        bettor = bettor.lower()
        bettor_teams = np.loadtxt(bettor + bet_file_postfix, dtype=str, delimiter='\t')

        bettor_obj = Bettor(bettor, order, bettor_teams)

        person_list += [bettor_obj]

    # Add new pick number to each team
    determine_current_pick_order(person_list)

    # Create graphs and html pages
    plot_graph_all(person_list)
    make_html(person_list)
    make_bettor_html(person_list)

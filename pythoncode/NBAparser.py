import urllib2
import json
import pandas as pd
import datetime as dt
import numpy as np

def getpage(htmlpage):

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(htmlpage)
    #response = urllib2.urlopen(htmlpage)
    html = response.read()
    response.close()
    return html


def makejson(json_text, alt=False, aftertrade=False):

    vicki_orig  = ['Spurs', 'Rockets', 'Grizzlies', 'Heat', 'Wizards', 
              'Bucks', 'Mavericks', 'Magic', 'Nets', 'Knicks']
    johnny_orig = ['Warriors', 'Thunder', 'Celtics', 'Pelicans', 'Bulls',
              'Jazz', 'Suns', 'Timberwolves', 'Nuggets', 'Lakers']
    taro_orig   = ['Cavaliers', 'Clippers', 'Hawks', 'Raptors', 'Hornets',
             'Pacers', 'Pistons', 'Kings', 'Blazers', '76ers']
              

    tradedate = 'March 16'
    
    # Thunder for Nets
    vicki_trade1  = ['Spurs', 'Rockets', 'Grizzlies', 'Heat', 'Wizards', 
              'Bucks', 'Mavericks', 'Magic', 'Thunder', 'Knicks']
    johnny_trade1 = ['Warriors', 'Nets', 'Celtics', 'Pelicans', 'Bulls',
              'Jazz', 'Suns', 'Timberwolves', 'Nuggets', 'Lakers']
    taro_trade1   = ['Cavaliers', 'Clippers', 'Hawks', 'Raptors', 'Hornets',
             'Pacers', 'Pistons', 'Kings', 'Blazers', '76ers']    



    if alt == True:
        vicki  = ['Spurs', 'Clippers', 'Hawks', 'Heat', 'Wizards', 
                'Rockets', 'Nuggets', 'Pelicans', '76ers', 'Knicks']
        johnny = ['Warriors', 'Raptors', 'Celtics', 'Grizzlies', 'Bulls',
                'Jazz', 'Pacers', 'Timberwolves', 'Kings', 'Lakers']
        taro   = ['Cavaliers', 'Thunder', 'Hornets', 'Mavericks', 'Blazers',
                'Magic', 'Pistons', 'Bucks', 'Suns', 'Nets']
    
    if aftertrade == True:
        vicki  = vicki_trade1
        johnny = johnny_trade1
        taro   = taro_trade1
        
    if aftertrade == False:
        vicki  = vicki_orig
        johnny = johnny_orig
        taro   = taro_orig
        
    #print vicki
               
    data = json.loads(json_text)
    
    vwins = 0; vloss = 0
    jwins = 0; jloss = 0
    twins = 0; tloss = 0
    for teamdata in data['resultSets'][0]['rowSet']:
        teamname = teamdata[1]
        teamwins = teamdata[3]
        teamloss = teamdata[4]
        
        if any(s in teamname for s in vicki):
            vwins += teamwins
            vloss += teamloss
        if any(s in teamname for s in johnny):
            jwins += teamwins
            jloss += teamloss
        if any(s in teamname for s in taro):
            twins += teamwins
            tloss += teamloss
    
    vwins_remain, jwins_remain, twins_remain = calc_remaining_wins(vicki, johnny, taro)
    
    #print teamname, teamwins,teamloss
    #print 'Vicki ', vwins, vloss, vwins_remain
    #print 'Johnny ', jwins, jloss, jwins_remain
    #print 'Taro ', twins, tloss, twins_remain

    return [[vwins,vloss,vwins_remain], 
            [jwins,jloss,jwins_remain],
            [twins,tloss,twins_remain]]
 
def calc_remaining_wins(vicki, johnny, taro):

    # Upload the current schedule
    nba_sched = pd.read_csv('/Users/vickitoy/Sideprojects/NBA-fantasy-league/pythoncode/2015_schedule.txt', index_col=0)
    
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
        
    
    
def parser(alt=False):
    #website = 'http://stats.nba.com/stats/leaguedashteamstats?Season=2015' +\
    #            '-16&AllStarSeason&SeasonType=Regular%20Season&LeagueID=00&' +\
    #            'MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&' +\
    #            'Rank=N&Outcome&Location&Month=0&SeasonSegment&DateFrom&Date' +\
    #            'To&OpponentTeamID=0&VsConference&VsDivision&GameSegment&' +\
    #            'Period=0&LastNGames=0&GameScope&PlayerExperience&Player' +\
    #            'Position&StarterBench'

    # Before trade date
    website_bt = 'http://stats.nba.com/stats/leaguedashteamstats?Season=2015' +\
                '-16&AllStarSeason&SeasonType=Regular%20Season&LeagueID=00&' +\
                'MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&' +\
                'Rank=N&Outcome&Location&Month=0&SeasonSegment&DateFrom&Date' +\
                'To=March15&OpponentTeamID=0&VsConference&VsDivision&GameSegment&' +\
                'Period=0&LastNGames=0&GameScope&PlayerExperience&Player' +\
                'Position&StarterBench'
                                
    #print website
    json_text = getpage(website_bt)
    [[vwins_bt,vloss_bt,vwins_remain_bt], 
     [jwins_bt,jloss_bt,jwins_remain_bt],
     [twins_bt,tloss_bt,twins_remain_bt]] = makejson(json_text, alt=alt, aftertrade=False)
    
    # After trade date
    website_at = 'http://stats.nba.com/stats/leaguedashteamstats?Season=2015' +\
                '-16&AllStarSeason&SeasonType=Regular%20Season&LeagueID=00&' +\
                'MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&' +\
                'Rank=N&Outcome&Location&Month=0&SeasonSegment&DateFrom=March16&Date' +\
                'To&OpponentTeamID=0&VsConference&VsDivision&GameSegment&' +\
                'Period=0&LastNGames=0&GameScope&PlayerExperience&Player' +\
                'Position&StarterBench'
                
    #print website
    json_text = getpage(website_at)
    [[vwins_at,vloss_at,vwins_remain_at], 
     [jwins_at,jloss_at,jwins_remain_at],
     [twins_at,tloss_at,twins_remain_at]]  = makejson(json_text, alt=alt, aftertrade=True)
    
    #print 'Vicki ', vwins_bt+vwins_at, vloss_bt+vloss_at, vwins_remain_at
    #print 'Johnny ', jwins_bt+jwins_at, jloss_bt+jloss_at, jwins_remain_at
    #print 'Taro ', twins_bt+twins_at, tloss_bt+tloss_at, twins_remain_at
    
   
    out = {'vwins':vwins_bt+vwins_at,'vloss':vloss_bt+vloss_at, 'vremain':vwins_remain_at,
          'jwins':jwins_bt+jwins_at,'jloss':jloss_bt+jloss_at, 'jremain':jwins_remain_at,
          'twins':twins_bt+twins_at,'tloss':tloss_bt+tloss_at, 'tremain':twins_remain_at }
          
    print json.dumps(out, sort_keys=True)
    
if __name__ == '__main__':
    parser()
    
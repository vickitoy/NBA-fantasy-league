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


def makejson(json_text):

    vicki  = ['Cavaliers', 'Clippers', 'Blazers', 'Grizzlies', 'Pacers',
                'Mavericks', 'Bulls', 'Heat', 'Suns', '76ers']
    johnny = ['Warriors', 'Celtics', 'Jazz', 'Hawks', 'Pistons',
               'Timberwolves', 'Bucks', 'Magic', 'Nuggets', 'Lakers']
    taro   = ['Spurs', 'Raptors', 'Rockets', 'Hornets','Thunder',
                'Wizards', 'Pelicans', 'Knicks', 'Kings', 'Nets']
    
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
    nba_sched = pd.read_csv('/Users/vickitoy/Sideprojects/NBA-fantasy-league/pythoncode/2016_schedule.txt', index_col=0)
    
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
    website = 'http://stats.nba.com/stats/leaguedashteamstats?Season=2016' +\
                '-17&AllStarSeason&SeasonType=Regular%20Season&LeagueID=00&' +\
                'MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&' +\
                'Rank=N&Outcome&Location&Month=0&SeasonSegment&DateFrom&Date' +\
                'To&OpponentTeamID=0&VsConference&VsDivision&GameSegment&' +\
                'Period=0&LastNGames=0&GameScope&PlayerExperience&Player' +\
                'Position&StarterBench'
                            
    #print website
    json_text = getpage(website)
    [[vwins,vloss,vwins_remain], 
     [jwins,jloss,jwins_remain],
     [twins,tloss,twins_remain]] = makejson(json_text)

   
    out = {'vwins':vwins,'vloss':vloss, 'vremain':vwins_remain,
          'jwins':jwins,'jloss':jloss, 'jremain':jwins_remain,
          'twins':twins,'tloss':tloss, 'tremain':twins_remain } 
    
    print json.dumps(out, sort_keys=True)   
    
if __name__ == '__main__':
    parser()

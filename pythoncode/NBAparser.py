import urllib2
import json

def getpage(htmlpage):
    response = urllib2.urlopen(htmlpage)
    html = response.read()
    response.close()
    return html
    

def makejson(json_text):

    vicki  = ['Spurs', 'Rockets', 'Grizzlies', 'Heat', 'Wizards', 
              'Bucks', 'Mavericks', 'Magic', 'Nets', 'Knicks']
    johnny = ['Warriors', 'Thunder', 'Celtics', 'Pelicans', 'Bulls',
              'Jazz', 'Suns', 'Timberwolves', 'Nuggets', 'Lakers']
    taro   = ['Cavaliers', 'Clippers', 'Hawks', 'Raptors', 'Hornets',
              'Pacers', 'Pistons', 'Kings', 'Blazers', '76ers']
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
        #print teamname, teamwins,teamloss
    print 'Vicki ', vwins, vloss
    print 'Johnny ', jwins, jloss
    print 'Taro ', twins, tloss

    
def parser():
    website = 'http://stats.nba.com/stats/leaguedashteamstats?Season=2015' +\
                '-16&AllStarSeason&SeasonType=Regular%20Season&LeagueID=00&' +\
                'MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&' +\
                'Rank=N&Outcome&Location&Month=0&SeasonSegment&DateFrom&Date' +\
                'To&OpponentTeamID=0&VsConference&VsDivision&GameSegment&' +\
                'Period=0&LastNGames=0&GameScope&PlayerExperience&Player' +\
                'Position&StarterBench'
    json_text = getpage(website)
    makejson(json_text)
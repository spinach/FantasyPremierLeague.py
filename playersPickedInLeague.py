import requests
import json
import unicodecsv as csv
import argparse
from tqdm import tqdm
import logging, sys


FPL_URL = "https://fantasy.premierleague.com/api/"
LOGIN_URL = "https://users.premierleague.com/accounts/login/"
USER_SUMMARY_SUBURL = "element-summary/"
LEAGUE_CLASSIC_STANDING_SUBURL = "leagues-classic/"
LEAGUE_H2H_STANDING_SUBURL = "leagues-h2h/"
TEAM_ENTRY_SUBURL = "entry/"
PLAYERS_INFO_SUBURL = "bootstrap-static/"
PLAYERS_INFO_FILENAME = "output/allPlayersInfo.json"
USERNAME = 'fantasy@netmail3.net' 
PASSWORD =  'FPLshow#123'

USER_SUMMARY_URL = FPL_URL + USER_SUMMARY_SUBURL
PLAYERS_INFO_URL = FPL_URL + PLAYERS_INFO_SUBURL
START_PAGE = 1

payload = {
    'login':USERNAME,
    'password':PASSWORD,
    'redirect_uri': 'https://fantasy.premierleague.com/',
    'app':'plfpl-web'
}
s = requests.session()
s.post(LOGIN_URL, data=payload)

# Download all player data: https://fantasy.premierleague.com/api/bootstrap-static
def getPlayersInfo():
    r = s.get(PLAYERS_INFO_URL)
    jsonResponse = r.json()
    with open(PLAYERS_INFO_FILENAME, 'w') as outfile:
        json.dump(jsonResponse, outfile)


# Get users in league:
# https://fantasy.premierleague.com/api/leagues-classic/43919/standings/?page_new_entries=1&page_standings=2&phase=1
def getUserEntryIds(league_id, ls_page, league_Standing_Url):
    entries = []
    while(True):
        league_url = league_Standing_Url + str(league_id) + "/standings/" + "?page_new_entries=1&page_standings=" + str(ls_page) + "&phase=1"
        r = s.get(league_url)
        jsonResponse = r.json()
        managers = jsonResponse["standings"]["results"]
        if not managers:
            print "Total managers :",len(entries)
            break

        for player in managers:
            entries.append(player["entry"])
        ls_page+=1

    return entries


# team picked by user. example: https://fantasy.premierleague.com/api/entry/2677936/event/1/picks with 2677936 being entry_id of the player
def getplayersPickedForEntryId(entry_id, GWNumber):
    eventSubUrl = "event/" + str(GWNumber) + "/picks/"
    playerTeamUrlForSpecificGW = FPL_URL + TEAM_ENTRY_SUBURL + str(entry_id) + "/" + eventSubUrl
    r = s.get(playerTeamUrlForSpecificGW)
    jsonResponse = r.json()
    try:
        picks = jsonResponse["picks"]
    except:
        if jsonResponse["detail"]:
            print "entry_id "+str(entry_id)+" doesn't have info for this gameweek" 
        return None, None
    elements = []
    captainId = 1
    for pick in picks:
        elements.append(pick["element"])
        if pick["is_captain"]:
            captainId = pick["element"]

    return elements, captainId

# read player info from the json file that we downlaoded
def getAllPlayersDetailedJson():
    with open(PLAYERS_INFO_FILENAME) as json_data:
        d = json.load(json_data)
        return d

# writes the results to csv file
def writeToFile(countOfplayersPicked, fileName):
    with open(fileName, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['name', 'num'])
        for row in countOfplayersPicked:
            csv_out.writerow(row)

# Main Script

parser = argparse.ArgumentParser(description='Get players picked in your league in a certain GameWeek')
parser.add_argument('-l','--league', help='league entry id', required=True)
parser.add_argument('-g','--gameweek', help='gameweek number', required=True)
parser.add_argument('-t', '--type', help='league type')
parser.add_argument('-d', '--debug', help='deubg mode on')
args = vars(parser.parse_args())

if args['debug']:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

getPlayersInfo()
playerElementIdToNameMap = {}
allPlayers = getAllPlayersDetailedJson()
for element in allPlayers["elements"]:
    playerElementIdToNameMap[element["id"]] = element["web_name"]#.encode('ascii', 'ignore')

countOfplayersPicked = {}
countOfCaptainsPicked = {}
totalNumberOfPlayersCount = 0
pageCount = START_PAGE
GWNumber = args['gameweek']
leagueIdSelected = args['league']

if args['type'] == "h2h":
    leagueStandingUrl = FPL_URL + LEAGUE_H2H_STANDING_SUBURL
    print("h2h league mode")
else:
    leagueStandingUrl = FPL_URL + LEAGUE_CLASSIC_STANDING_SUBURL
    print("classic league mode")


try:
    entries = getUserEntryIds(leagueIdSelected, pageCount, leagueStandingUrl)
except Exception, err:
    print "Error occured in getting entries/managers in the league."
    print err
    raise

for entry in tqdm(entries):
    try:
        elements, captainId = getplayersPickedForEntryId(entry, GWNumber)
    except Exception, err:
        print "Error occured in getting palyers and captain of the entry/manager"
        print err
        raise
    if not elements:
        continue
    for element in elements:
        name = playerElementIdToNameMap[element]
        if name in countOfplayersPicked:
            countOfplayersPicked[name] += 1
        else:
            countOfplayersPicked[name] = 1

    captainName = playerElementIdToNameMap[captainId]
    if captainName in countOfCaptainsPicked:
        countOfCaptainsPicked[captainName] += 1
    else:
        countOfCaptainsPicked[captainName] = 1

listOfcountOfplayersPicked = sorted(countOfplayersPicked.items(), key=lambda x: x[1], reverse=True)
writeToFile(listOfcountOfplayersPicked, "output/GW"+str(GWNumber)+" Players "+str(leagueIdSelected)+".csv")
listOfCountOfCaptainsPicked = sorted(countOfCaptainsPicked.items(), key=lambda x: x[1], reverse=True)
writeToFile(listOfCountOfCaptainsPicked, "output/GW"+str(GWNumber)+" Captains "+str(leagueIdSelected)+".csv")

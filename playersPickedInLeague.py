import requests
import json
import csv
import argparse

FPL_URL = "https://fantasy.premierleague.com/drf/"
USER_SUMMARY_SUBURL = "element-summary/"
LEAGUE_CLASSIC_STANDING_SUBURL = "leagues-classic-standings/"
LEAGUE_H2H_STANDING_SUBURL = "leagues-h2h-standings/"
TEAM_ENTRY_SUBURL = "entry/"
PLAYERS_INFO_SUBURL = "bootstrap-static"
PLAYERS_INFO_FILENAME = "allPlayersInfo.json"

USER_SUMMARY_URL = FPL_URL + USER_SUMMARY_SUBURL
PLAYERS_INFO_URL = FPL_URL + PLAYERS_INFO_SUBURL
START_PAGE = 1

# Download all player data: https://fantasy.premierleague.com/drf/bootstrap-static
def getPlayersInfo():
    r = requests.get(PLAYERS_INFO_URL)
    jsonResponse = r.json()
    with open(PLAYERS_INFO_FILENAME, 'w') as outfile:
        json.dump(jsonResponse, outfile)


# Get users in league: https://fantasy.premierleague.com/drf/leagues-classic-standings/336217?phase=1&le-page=1&ls-page=5
def getUserEntryIds(league_id, ls_page, league_Standing_Url):
    league_url = league_Standing_Url + str(league_id) + "?phase=1&le-page=1&ls-page=" + str(ls_page)
    r = requests.get(league_url)
    jsonResponse = r.json()
    standings = jsonResponse["standings"]["results"]
    if not standings:
        print("no more standings found!")
        return None

    entries = []

    for player in standings:
        entries.append(player["entry"])

    return entries


# team picked by user. example: https://fantasy.premierleague.com/drf/entry/2677936/event/1/picks with 2677936 being entry_id of the player
def getplayersPickedForEntryId(entry_id, GWNumber):
    eventSubUrl = "event/" + str(GWNumber) + "/picks"
    playerTeamUrlForSpecificGW = FPL_URL + TEAM_ENTRY_SUBURL + str(entry_id) + "/" + eventSubUrl
    r = requests.get(playerTeamUrlForSpecificGW)
    jsonResponse = r.json()
    picks = jsonResponse["picks"]
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
args = vars(parser.parse_args())

getPlayersInfo()
playerElementIdToNameMap = {}
allPlayers = getAllPlayersDetailedJson()
for element in allPlayers["elements"]:
    playerElementIdToNameMap[element["id"]] = element["web_name"].encode('ascii', 'ignore')

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

while (True):
    try:
        entries = getUserEntryIds(leagueIdSelected, pageCount, leagueStandingUrl)
        if entries is None:
            print("breaking as no more player entries")
            break

        totalNumberOfPlayersCount += len(entries)
        print("parsing pageCount: " + str(pageCount) + " with total number of players so far:" + str(
            totalNumberOfPlayersCount))
        for entry in entries:
            elements, captainId = getplayersPickedForEntryId(entry, GWNumber)
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
        writeToFile(listOfcountOfplayersPicked, "result playersPicked " + str(leagueIdSelected) + ".csv")
        listOfCountOfCaptainsPicked = sorted(countOfCaptainsPicked.items(), key=lambda x: x[1], reverse=True)
        writeToFile(listOfCountOfCaptainsPicked, "result captain " + str(leagueIdSelected) + ".csv")

        pageCount += 1
    except Exception, e:
        print str(e)
        pass

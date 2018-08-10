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


getPlayersInfo()
playerElementIdToNameMap = {}
allPlayers = getAllPlayersDetailedJson()
playerElementIdToNameMap[0] = ",".join(["Name", "Position", "Total Score", "Minutes Played", "Cost", "points_per_game", "points_per_game_per_million", "Bonus per 90", "Points per 90", "Points per million", "Points per million per 90"])
for element in allPlayers["elements"]:
    if element["minutes"] < 1000:
        continue
    totalScore = element["total_points"]
    minutesPlayed = element["minutes"]
    cost = element["now_cost"] / 10.0
    position = element["element_type"]
    points_per_game = float(element["points_per_game"])
    points_per_game_per_million = round(points_per_game / cost, 2)
    appearances = minutesPlayed / 90.0
    pointsPer90 = round(totalScore / appearances, 2)
    pointsPerMillion = round(totalScore / cost, 2)
    pointsPerMillionPer90 = round(pointsPer90 / cost, 2)
    bonusPer90 = round(element["bonus"] / appearances, 2)
    name = element["web_name"].encode('ascii', 'ignore')
    playerElementIdToNameMap[element["id"]] = ",".join([name, str(position), str(totalScore), str(minutesPlayed), str(cost), str(points_per_game), str(points_per_game_per_million), str(bonusPer90), str(pointsPer90), str(pointsPerMillion), str(pointsPerMillionPer90)])

print(playerElementIdToNameMap)
with open("ppm.csv", 'w') as f:
    for key, value in playerElementIdToNameMap.items():
        f.write(value + "\n")

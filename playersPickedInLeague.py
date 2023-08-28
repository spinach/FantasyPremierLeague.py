import argparse  # noqa 401
import json
import logging
import sys

import requests
import unicodecsv as csv
from tqdm import tqdm

FPL_URL = "https://fantasy.premierleague.com/api/"
LOGIN_URL = "https://users.premierleague.com/accounts/login/"
USER_SUMMARY_SUBURL = "element-summary/"
LEAGUE_CLASSIC_STANDING_SUBURL = "leagues-classic/"
LEAGUE_H2H_STANDING_SUBURL = "leagues-h2h/"
TEAM_ENTRY_SUBURL = "entry/"
PLAYERS_INFO_SUBURL = "bootstrap-static/"
PLAYERS_INFO_FILENAME = "output/allPlayersInfo.json"
USERNAME = "fantasy@netmail3.net"
PASSWORD = "FPLshow#123"

USER_SUMMARY_URL = FPL_URL + USER_SUMMARY_SUBURL
PLAYERS_INFO_URL = FPL_URL + PLAYERS_INFO_SUBURL
START_PAGE = 1

PAYLOAD = {
    "login": USERNAME,
    "password": PASSWORD,
    "redirect_uri": "https://fantasy.premierleague.com/",
    "app": "plfpl-web",
}
session = requests.session()
session.post(LOGIN_URL, data=PAYLOAD)


def getPlayersInfo():
    # Download all player data: https://fantasy.premierleague.com/api/bootstrap-static
    result = session.get(PLAYERS_INFO_URL)
    with open(PLAYERS_INFO_FILENAME, "w") as outfile:
        json.dump(result.json(), outfile)


def getUserEntryIds(league_id, page_count, league_standing_url):
    # Get users in league:
    # https://fantasy.premierleague.com/api/leagues-classic/43919/standings/?page_new_entries=1&page_standings=2&phase=1
    entries = []
    while True:
        league_url = (
            league_standing_url
            + str(league_id)
            + "/standings/"
            + "?page_new_entries=1&page_standings="
            + str(page_count)
            + "&phase=1"
        )
        result = session.get(league_url)
        managers = result.json()["standings"]["results"]
        if not managers:
            print("Total managers :", len(entries))
            break

        for player in managers:
            entries.append(player["entry"])

        page_count += 1

    return entries


def getplayersPickedForEntryId(entry_id, GWNumber):
    # team picked by user. example: https://fantasy.premierleague.com/api/entry/2677936/event/1/picks with 2677936 being entry_id of the player # noqa 501
    eventSubUrl = "event/" + str(GWNumber) + "/picks/"
    playerTeamUrlForSpecificGW = (
        FPL_URL + TEAM_ENTRY_SUBURL + str(entry_id) + "/" + eventSubUrl
    )

    result = session.get(playerTeamUrlForSpecificGW).json()
    try:
        picks = result["picks"]
    except Exception as e:
        print(e)
        if result["detail"]:
            print("entry_id " + str(entry_id) + " doesn't have info for this gameweek")
        return None, None

    elements = []
    captainId = 1
    for pick in picks:
        elements.append(pick["element"])
        if pick["is_captain"]:
            captainId = pick["element"]

    return elements, captainId


def getAllPlayersDetailedJson():
    # read player info from the json file that we downloaded
    with open(PLAYERS_INFO_FILENAME) as json_data:
        return json.load(json_data)


def writeToFile(countOfplayersPicked, fileName):
    # writes the results to csv file
    with open(fileName, "w") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["name", "num"])
        for row in countOfplayersPicked:
            csv_out.writerow(row)


def main():
    # Main Script
    parser = argparse.ArgumentParser(
        description="Get players picked in your league in a certain GameWeek",
    )
    parser.add_argument("-l", "--league", help="league entry id", required=True)
    parser.add_argument("-g", "--gameweek", help="gameweek number", required=True)
    parser.add_argument("-t", "--type", help="league type")
    parser.add_argument("-d", "--debug", help="deubg mode on")
    args = vars(parser.parse_args())

    if args["debug"]:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    getPlayersInfo()
    playerElementIdToNameMap = {}
    allPlayers = getAllPlayersDetailedJson()
    for element in allPlayers["elements"]:
        playerElementIdToNameMap[element["id"]] = element["web_name"]

    countOfplayersPicked = {}
    countOfCaptainsPicked = {}
    GWNumber = args["gameweek"]
    leagueIdSelected = args["league"]

    if args["type"] == "h2h":
        leagueStandingUrl = FPL_URL + LEAGUE_H2H_STANDING_SUBURL
        print("h2h league mode")
    else:
        leagueStandingUrl = FPL_URL + LEAGUE_CLASSIC_STANDING_SUBURL
        print("classic league mode")

    try:
        entries = getUserEntryIds(leagueIdSelected, START_PAGE, leagueStandingUrl)
    except Exception as e:
        print("Error occured in getting entries/managers in the league.")
        print(e)
        raise

    for entry in tqdm(entries):
        try:
            elements, captainId = getplayersPickedForEntryId(entry, GWNumber)
        except Exception as e:
            print("Error occured in getting palyers and captain of the entry/manager")
            print(e)
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

    listOfcountOfplayersPicked = sorted(
        countOfplayersPicked.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    writeToFile(
        listOfcountOfplayersPicked,
        "output/GW" + str(GWNumber) + " Players " + str(leagueIdSelected) + ".csv",
    )

    listOfCountOfCaptainsPicked = sorted(
        countOfCaptainsPicked.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    writeToFile(
        listOfCountOfCaptainsPicked,
        "output/GW" + str(GWNumber) + " Captains " + str(leagueIdSelected) + ".csv",
    )


if __name__ == "__main__":
    main()

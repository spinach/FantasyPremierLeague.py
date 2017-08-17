# ⚽ FantasyPremierLeague-Api-Python

FantasyPremierLeague-Api-Python helps you access the data of the [Fantasy PremierLeague game](https://fantasy.premierleague.com/). It is intended for use by people who want to get satistical data around the game for fun. For now, there is a cool example where you can get interesting statistics about your mini league.

For now, you can get 2 main things out of the python script:

* Distribution of players that are being picked in a specific League and GameWeek
* Distribution of players being captained in a specific League and GameWeek

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisities

After cloning the project, you need to have Python 2.7 installed on your machine. Go to [Download Python 2.7.12](https://www.python.org/downloads/)

_If you want to use Python 3, check branch [python3](https://github.com/spinach/FantasyPremierLeague-Api.py/tree/python3)._

You also need to have the `requests` library on your machine. Run the following on your terminal:

```
pip install requests
```

### Usage

For now, you can get 2 main things out of the python script:

* Distribution of players that are being picked in a specific League and GameWeek
* Distribution of players being captained in a specific League and GameWeek

Follow these easy steps to get these results for your league:

1. Go to [https://fantasy.premierleague.com/](https://fantasy.premierleague.com/) and login.
2. Go to leagues, and then click on the league you want to analyse
3. Check out the URL. It will be something like https://fantasy.premierleague.com/a/leagues/standings/336217/classic. Save the 336217 number, which is your league entry id.
4. Decide what GameWeek you want to analyse, let's say it's 2, and then check what type of league it is (whether h2h or classic)
5. Run the following command at the root of your project by inserting your specific league entry Id and Gameweek Number: `python playersPickedInLeague.py --league 336217 --gameweek 2 --type classic` or `python playersPickedInLeague.py -l 336217 -g 2 -t classic`. For h2h leagues, replace `classic` with `h2h`.

_Warning: If you get an SSLError issue, then try using the [python3 branch](https://github.com/spinach/FantasyPremierLeague-Api.py/tree/python3). More details about the issue can be found in #2._

Voila, you should be able to see 2 csv files created at the root of your project

### How to Contribute
This is just an example of what you can do with the fpl apis. I'm sure there are lots of cool ideas, so feel free to suggest by submitting an issue, or even write it yourself and send me a PR :)

### TODO

- Offer this script on a website so that anyone can enter his own Ids

# ⚽ FantasyPremierLeague-Api-Python

FantasyPremierLeague-Api-Python helps you access the data of the [Fantasy PremierLeague game](https://fantasy.premierleague.com/). It is intended for use by people who want to get satistical data around the game for fun. For now, there is a cool example where you can get interesting statistics about your mini league.

For now, you can get 2 main things out of the python script:

- Distribution of players that are being picked in a specific League and GameWeek
- Distribution of players being captained in a specific League and GameWeek

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisities

After cloning the project, you need to have Python 3.4 installed on your machine. Go to [Download Python 3.4.7](https://www.python.org/downloads/)

You also need to have the `requests` and `tqdm` library on your machine. Run the following on your terminal:

```
pip3 install -r requirements.txt
```

Or you can install individually by

```
pip3 install requests tqdm
```

### Usage

For now, you can get 2 main things out of the python script:

- Distribution of players that are being picked in a specific League and GameWeek
- Distribution of players being captained in a specific League and GameWeek

Follow these easy steps to get these results for your league:

1. Go to [https://fantasy.premierleague.com/](https://fantasy.premierleague.com/) and login.
2. Go to leagues, and then click on the league you want to analyse
3. Check out the URL. It will be something like https://fantasy.premierleague.com/a/leagues/standings/336217/classic. Save the 336217 number, which is your league entry id.
4. Decide what GameWeek you want to analyse, let's say it's 2, and then check what type of league it is (whether h2h or classic)
5. Run the following command at the root of your project by inserting your specific league entry Id and Gameweek Number: `python3 playersPickedInLeague.py --league 336217 --gameweek 2 --type classic` or `python3 playersPickedInLeague.py -l 336217 -g 2 -t classic`. For h2h leagues, replace `classic` with `h2h`.

Voila, you should be able to see 2 csv files created at the output folder of your project

Also if you want to run in deubg mode now add argument `-d True` or `--debug True` in above command line

### How to Contribute

This is just an example of what you can do with the fpl apis. I'm sure there are lots of cool ideas, so feel free to suggest by submitting an issue, or even write it yourself and send me a PR :)

### TODO

- Offer this script on a website so that anyone can enter his own Ids

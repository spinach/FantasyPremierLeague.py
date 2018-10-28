__author__ = 'guydaher'

import re

from bs4 import BeautifulSoup


import requests

url = "https://understat.com/league/EPL"

r = requests.get(url)

data = r.text

soup = BeautifulSoup(data, "html.parser")

scripts = soup.find_all("script")

for script in scripts:
    if "playersData" in str(script):
        playersDataScript = str(script)
playersData = playersDataScript.decode('string_escape')

playersData = playersData.split("JSON.parse('", 1)[1]
playersData = playersData.split("');", 1)[0]

# print(playersData)

with open("understat.txt", "w") as text_file:
    text_file.write(playersData)





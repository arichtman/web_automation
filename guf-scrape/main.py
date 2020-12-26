

# %% Setup

import csv
import requests
import urllib.request
import time
import re
from bs4 import BeautifulSoup

# %%


def getRating(name):
    tmpName = re.sub(r'[^\w\d\s]+', '', name)
    tmpName = tmpName.replace(
        'Kickstarter', '').replace('Edition', '')
    tmpName = tmpName.replace(' ', '%20')
    url = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q=" + tmpName
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    topResult = soup.find('tr', {'id': 'row_'})
    if topResult is None:
        url = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q=" + \
            name.replace(' ', '%20')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        topResult = soup.find('tr', {'id': 'row_'})
        if topResult is None:
            return 'none found'
    avgRating = topResult.find('td', {'class': 'collection_bggrating'})
    return avgRating.contents[0].strip()

# %%


libArr = []
for pageNum in range(1, 35):
    url = 'https://guf.com.au/collections/clearance?page=' + str(pageNum)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    productsBulk = soup.findAll(
        'div', {'class': ['col-md-3'], 'data-price': re.compile('.*')})

    for game in productsBulk:
        gameDict = {'name': [], 'price': [], 'rating': []}
        gameName = game.find(
            'p', {'class': 'productTitle'}).contents[0].strip()
        gameDict["name"] = gameName

        gameDict['price'] = game['data-price']
        gameDict['rating'] = getRating(gameName)
        libArr.append(gameDict)

# %%

# Count the failed searches (for development, mostly)
print(len(libArr))
print(len(list(filter(lambda d: d['rating'] == 'none found', libArr))))

# %%

# Dump out our data
keys = libArr[0].keys()
with open('games.csv', 'w', newline='', encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(libArr)

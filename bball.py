from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import re

statTypes = ["pts", "ast", "rbd", "stl", "blk"]

date = str(date.today() - timedelta(days = 1))
month = date.split("-")[1]
day = date.split("-")[2]
year = date.split("-")[0]

url = f"https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"
page = requests.get(url)
doc = BeautifulSoup(page.text, "html.parser")

print("\nGAMES PLAYED")

div = doc.find(class_="game_summaries")
games = doc.find_all(class_="game_summary expanded nohover")
for game in games:
    winner = game.find(class_="winner")
    wscore = winner.find(class_="right")
    loser = game.find(class_="loser")
    lscore = loser.find(class_="right")

    print(winner.a.text + " d. " + loser.a.text + " " + wscore.text + "-" + lscore.text)

    bs_url = game.find(class_="links").a["href"]
    url = f"https://www.basketball-reference.com{bs_url}"
    page = requests.get(url)
    doc = BeautifulSoup(page.text, "html.parser")

    stats = { }
    for boxscore in doc.find_all(text=re.compile("Basic and Advanced Stats Table")):
        table = boxscore.parent.parent.tbody
        players = table.find_all(class_="left")
        for player in players:
            name = player.a.text.split(" ")[1]
            for row in player.next_siblings:
                if row.get('data-stat') == "trb":
                    rbd = row.text
                if row.get('data-stat') == "ast":
                    ast = row.text
                if row.get('data-stat') == "stl":
                    stl = row.text
                if row.get('data-stat') == "blk":
                    blk = row.text
                if row.get('data-stat') == "pts":
                    pts = row.text
            stats[name] = {"pts": int(pts), "ast": int(ast), "rbd": int(rbd), "stl": int(stl), "blk": int(blk)}
    
    print("LEADERS BY STATISTIC")
    for x in range(5):
        a = statTypes[x]
        s = sorted(stats.items(), key=lambda x: x[1][a], reverse=True)
        leader = s[0]
        print(a.upper() + ": " + leader[0] + " " + str(leader[1]['pts']) + "/" + str(leader[1]['ast']) + "/" + str(leader[1]['rbd']) + "/" + 
            str(leader[1]['stl']) + "/" + str(leader[1]['blk']))
        
    print()

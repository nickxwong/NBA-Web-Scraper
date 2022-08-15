from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import re

report = ''

# Yesterday's games
# get yesterday's date 
date = str(date.today() - timedelta(days = 1))
month = date.split('-')[1]
day = date.split('-')[2]
year = date.split('-')[0]

report += f'YESTERDAY ({month}/{day}/{year}) IN THE NBA\n'
report += '---------------------\n\n'
report += f'GAMES PLAYED\n'

# get scores of all games played yesterday
url = f'https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}'
html = BeautifulSoup(requests.get(url).text, 'html.parser')

if html.find(string='No games played on this date.') != None:
    report += 'No games were played yesterday :(\n'
else:
    games_played = html.find_all(class_='game_summary expanded nohover')
    i = 1
    for game in games_played:
        winner = game.find(class_='winner')
        winner_score = winner.find(class_='right').text
        loser = game.find(class_='loser')
        loser_score = loser.find(class_='right').text

        report += f'[{i}] {winner.a.text} d. {loser.a.text} {winner_score}-{loser_score}\n'
        i += 1

        # get box score of the game
        url = game.find(class_='links').a['href']
        html = BeautifulSoup(requests.get(f'https://www.basketball-reference.com{url}').text, 'html.parser')

        player_stats = []
        for boxscore in html.find_all(text=re.compile('Basic and Advanced Stats Table')):
            table = boxscore.parent.parent.tbody
            players = table.find_all(class_='left')
            for player in players:
                name = player.a.text.split(' ')[1]
                for row in player.next_siblings:
                    if (row.get('data-stat') == 'trb'):
                        rbd = row.text
                    if (row.get('data-stat') == 'ast'):
                        ast = row.text
                    if (row.get('data-stat') == 'stl'):
                        stl = row.text
                    if (row.get('data-stat') == 'blk'):
                        blk = row.text
                    if (row.get('data-stat') == 'pts'):
                        pts = row.text
                player_stats.append((name, int(pts), int(ast), int(rbd), int(stl), int(blk)))
        
        statTypes = ['pts', 'ast', 'rbd', 'stl', 'blk']
        for x in range(5):
            a = statTypes[x]
            player_stats.sort(reverse=True, key=lambda player: player[x + 1])
            leader = player_stats[0]
            report += f'    * {leader[0]} was the {a.upper()} leader with {str(player_stats[0][x + 1])} {a}\n'
        
        report += '\n'

# r/NBA subreddit
report += '\nTOP 5 POSTS ON r/NBA\n'
html = BeautifulSoup(requests.get('https://old.reddit.com/r/nba/', headers={'User-agent': '1'}).text, 'html.parser')

# assemble all posts on r/NBA's front page into a list
today_posts = []
posts = html.select('.thing:not(.promoted)')
for post in posts:
    title = post.find('a', class_='title').text
    upvotes = post.find(class_='score unvoted').text
    url = post.find('a')['href']
    today_posts.append((title, int(upvotes) if upvotes != '•' else 0, url))

# sort list by number of upvotes
today_posts.sort(reverse=True, key=lambda post: post[1])

for x in range(5):
    report += f'[{x + 1}] {today_posts[x][0]}\n'
    # add url 
    url = today_posts[x][2]
    if url.startswith('/r/nba/'):
        url = 'https://www.reddit.com' + url
    report += f'{url}\n' 

print(report)

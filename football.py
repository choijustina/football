'''
change date of NFL_SUNDAY if not running on Sunday

$ python3 football.py
'''

from bs4 import BeautifulSoup
import datetime
import requests
import sys


# /teams?s={"$query":{"season":2015},"$take":40}&fs={id,season,fullName,nickName,abbr,teamType,conference{abbr},division{abbr}}
# http://www.nfl.com/liveupdate/scores/scores.json
# http://www.nfl.com/liveupdate/scorestrip/ss.xml

NFL_SUNDAY = datetime.datetime.today().strftime('%Y%m%d')
NAME = 'football_' + NFL_SUNDAY + '.txt'
OUTPUT = open(NAME, 'w+')

def getNFLData():
	response = requests.get("http://www.nfl.com/liveupdate/scores/scores.json")
	headers = response.headers
	if response.status_code != 200:
		print('getNFLData request unsuccessful %s' % (response.status_code))
		return
	return response.json()

def printResults(gameData):
	OUTPUT.write('\t1\t2\t3\t4\tFinal\n')
	OUTPUT.write(\
		gameData['home']['abbr'] + '\t' +
		str(gameData['home']['score']['1']) + '\t' +
		str(gameData['home']['score']['2']) + '\t' +
		str(gameData['home']['score']['3']) + '\t' +
		str(gameData['home']['score']['4']) + '\t' +
		str(gameData['home']['score']['T']) + '\t' + '\n'
		)
	OUTPUT.write(\
		gameData['away']['abbr'] + '\t' +
		str(gameData['away']['score']['1']) + '\t' +
		str(gameData['away']['score']['2']) + '\t' +
		str(gameData['away']['score']['3']) + '\t' +
		str(gameData['away']['score']['4']) + '\t' +
		str(gameData['away']['score']['T']) + '\t' + '\n'
		)
	OUTPUT.write('\n')

def doNFL():
	json = getNFLData()

	# THURSDAY GAME
	thurs = str(int(NFL_SUNDAY) - 3) + '00'
	OUTPUT.write('Thurs ' + thurs[4:6] + '/' + thurs[6:8] + '\n')
	printResults(json[thurs])

	# SUNDAY GAMES
	for gameNum in range(0,13):
		if gameNum < 10:
			date = NFL_SUNDAY + '0' + str(gameNum)
		else:
			date = NFL_SUNDAY + str(gameNum)
		OUTPUT.write('Sun ' + date[4:6] + '/' + date[6:8] + '\n')
		try:
			printResults(json[date])
		except KeyError:
			print('game ' + date + ' not found')
			continue

	# MONDAY GAME
	mon = str(int(NFL_SUNDAY) + 1) + '00'
	OUTPUT.write('Mon ' + mon[4:6] + '/' + mon[6:8] + '\n')
	printResults(json[mon])
	
	return

def getNFLStandings():
	print('Doing NFL Standings')
	filename = 'nflstandings_' + NFL_SUNDAY + '.txt'
	try:
		file = open(filename)
		rawhtml = file.read()
		file.close()
	except FileNotFoundError:
		print(filename + ' not found; making request')
		rawhtml = requests.get('https://www.foxsports.com/nfl/standings').text
		newfile = open(filename, 'w+')
		newfile.write(rawhtml)
		newfile.close()

	html = BeautifulSoup(rawhtml, 'html.parser')
	tableRows = html.find_all('tr')
	OUTPUT.write('\n')
	OUTPUT.write(tableRows[0].find_all('th')[0].string.strip() + ' Standings as of ' + NFL_SUNDAY + '\n')

	afc = True
	nfc = False
	for row in range(1, len(tableRows)):
		if tableRows[row].find_all('th'):
			if afc and row % 6 == 0:
				continue
			elif nfc and row % 6 == 2:
				continue
			# division = tableRows[row].find_all('th', {'title': 'Team'})[0].string.strip()
			division = tableRows[row].find_all('th')[0].string.strip()
			if division == 'National Football Conference':
				nfc = True
				continue
			OUTPUT.write('\n' + division + '\n\t\t')
			for i in range(1, len(tableRows[row].find_all('th'))):
				OUTPUT.write(tableRows[row].find_all('th')[i].string.strip() + '\t')
			OUTPUT.write('\n')
		elif tableRows[row].find_all('span'): 	# print team name
			teamName = tableRows[row].find_all('span')[0].string
			if len(teamName) < 8:
				teamName = teamName + '\t'
			OUTPUT.write(teamName + '\t')
			tds = tableRows[row].find_all('td')		# stats
			for i in range(1, len(tds)):
				OUTPUT.write(tds[i].string + '\t')
			OUTPUT.write('\n')
		else:
			OUTPUT.write('\n')

	return

def doPac12():
	filename = 'pac12standings_' + NFL_SUNDAY + '.txt'
	try:
		file = open(filename)
		rawhtml = file.read()
		file.close()
	except FileNotFoundError:
		print(filename + ' not found; making request')
		rawhtml = requests.get('https://pac-12.com/football/standings').text
		newfile = open(filename, 'w+')
		newfile.write(rawhtml)
		newfile.close()

	html = BeautifulSoup(rawhtml, 'html.parser')
	OUTPUT.write(html.find_all('div', {'class': 'standings-updated'})[0].string)
	tableRows = html.find_all('tr')
	tblData = []
	tblData.append(
		['Team', 'Conference', 'Overall', 'LastGame', 'NextGame']
		)
	for row in range(1, len(tableRows)):
		if row == 7:
			continue
		if tableRows[row].find_all('span', {'class': 'ranking'}):
			ranking = tableRows[row].find_all('span', {'class': 'ranking'})[0].string + ' '
		else:
			ranking = ''
		team = tableRows[row].find_all('a')[1].string
		conference = tableRows[row].find_all('td', {'class': 'conference-wins'})[0].string
		overall = tableRows[row].find_all('td', {'class': 'overall-wins'})[0].string
		lastgame = tableRows[row].find_all('td', {'class': 'last-game'})[0].find_all('span')[0].string
		lastgame = lastgame.strip() + ' ' + tableRows[row].find_all('td', {'class': 'last-game'})[0].find_all('a')[0].string
		nextgame = tableRows[row].find_all('td', {'class': 'next-game'})[0].find_all('a')[0].find_all('span')[0].string
		nextgame = nextgame + ' ' + tableRows[row].find_all('td', {'class': 'next-game'})[0]['onclick'].split('/')[-1][:-2]

		tblData.append(
			[ranking + team, conference, overall, lastgame, nextgame]
			)
	
	width = max(len(word) for row in tblData for word in row)
	flag = True
	for row in tblData:
		team, conference, overall, lastgame, nextgame = row
		if team in ['USC', 'Colorado', 'Utah', 'Arizona', 'Arizona State', 'UCLA'] and flag:
			OUTPUT.write('\n')
			flag = False # don't print newline for south teams
		OUTPUT.write(''.join(team.ljust(width)) +
			conference.ljust(12) + 
			overall + '\t' +
			lastgame + '\t' +
			nextgame + '\n'
			)
	OUTPUT.write('\n')
	return

def doRankings():
	filename = 'rankings_' + NFL_SUNDAY + '.txt'
	try:
		file = open(filename)
		rawhtml = file.read()
		file.close()
	except FileNotFoundError:
		print(filename + ' not found; making request')
		source = 'http://www.espn.com/college-football/rankings'
		OUTPUT.write('source: ' + source + '\n')
		rawhtml = requests.get(source).text
		newfile = open(filename, 'w+')
		newfile.write(rawhtml)
		newfile.close()
	html = BeautifulSoup(rawhtml, 'html.parser')

	count = 1
	for team in html.find_all('span', {'class': 'team-names'}):
		name = team.string
		OUTPUT.write(str(count) + ' ' + name + '\n')
		count += 1
		if count == 26:
			break

def main():
	doNFL()
	OUTPUT.write('\n')
	getNFLStandings()
	OUTPUT.write('\n')
	doPac12()
	OUTPUT.write('\n')
	doRankings()

	OUTPUT.close()


if __name__ == '__main__':
	main()

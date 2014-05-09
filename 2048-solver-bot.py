import os, time, re, sys, csv, datetime, timeit, argparse
import numpy as np
from operator import itemgetter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class gamesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) :
        if values <= 0 or values > 1000 :
            parser.error("Games to play number should been in range 1..1000")
            #raise argparse.ArgumentError("Minimum bandwidth is 12")
        setattr(namespace, self.dest, values)

class noteAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) :
        if isinstance(values, basestring) == False :
        	parser.error("Please, use quotes \" \" to determine you note as argument")
        if len(values) > 140 :
            parser.error("Too long note. Make it Twitter-way with no longer than 140 chars")
            #raise argparse.ArgumentError("Minimum bandwidth is 12")
        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser(description="This bot will try to solve 2048 puzzle game which hosted on http://gabrielecirulli.github.io/2048/")
parser.add_argument("-p", "--play", help="immediately starts playing", action="store_true")
parser.add_argument("-g", "--games", help="play exact X games", action=gamesAction, metavar="X", type=int, default=1)
parser.add_argument("-n", "--note", help="short note string (<140chrs) in \"quotes\" will add to csv with each game result", action=noteAction, metavar="STR", type=str, default="")
parser.add_argument("-d", "--debug", help="reserved for debugging purposes", action="store_true")
args = parser.parse_args()
#ArgDict = vars(args)

chromedriver = "/Users/user/Downloads/chromedriver"		#tricky part depends on bug in Python/Selenium, SO it
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

driver.get("http://gabrielecirulli.github.io/2048/")
assert "2048" in driver.title

Version = "0.1.3"
Garden = np.zeros((4, 4), dtype=np.int)		#global matrix for storing tiles state
TimerStart, TimerStop = 0, 0
CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft = 0, 0, 0, 0, 0
InternalScore, ScoreCheck = 0, 0
CounterGames = args.games

def gameTimer(standbyG):		#game stopwatch
	global TimerStart, TimerStop
	overall = 0
	if standbyG == "start":
		TimerStart = timeit.default_timer()
	elif standbyG == "stop":
		TimerStop = timeit.default_timer()
	elif standbyG == "tps":
		overall = TimerStop - TimerStart
		t = time.strftime('%M:%S', time.localtime(overall))
		return sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))		#manually convert to total seconds
	elif standbyG == "show":
		overall = TimerStop - TimerStart
		return time.strftime('%M:%S', time.localtime(overall))

def logToFile():
	with open('ResultLog.csv', 'a',) as fp:		#write results to the file
	    a = csv.writer(fp, delimiter=',')
	    data = [Version, 
	    		datetime.datetime.now().strftime("%d%B%Y %H:%M:%S"), 
	    		getPubScore(), 
	    		np.amax(Garden), 										#max tile
	    		gameTimer("show"), 										#time spent
	    		round(CounterTurn / float(gameTimer("tps")), 2),		#turns per secons
	    		CounterTurn, 											#turns total
	    		round(float(CounterTurnDown) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnRight) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnUp) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnLeft) / CounterTurn * 100, 1), 
	    		flattenGarden(),
	    		args.note]
	    a.writerow(data)

def printSummary():		#print summary after game finished
	print " "
	printMatrix(Garden)
	print " "
	print "Score:         " + getPubScore()
	print "Score check:   " + str(ScoreCheck)
	print "MaxTile:       " + str(np.amax(Garden))		#flatten Garden and found max tile
	print "Turns total:   " + str(CounterTurn)
	print "       down:   " + str(round(float(CounterTurnDown) / CounterTurn * 100, 1)) + "%"
	print "      right:   " + str(round(float(CounterTurnRight) / CounterTurn * 100, 1)) + "%"
	print "         up:   " + str(round(float(CounterTurnUp) / CounterTurn * 100, 1)) + "%"
	print "       left:   " + str(round(float(CounterTurnLeft) / CounterTurn * 100, 1)) + "%"
	print "Time (m:s):    " + gameTimer("show")
	print "Turns per sec: " + str(round(CounterTurn / float(gameTimer("tps")), 2))
	print " "

def getPubScore():		#get game score
	score = driver.find_element_by_class_name("score-container")
	pubScore = re.split('\+', score.get_attribute("innerText"))		#split string on "+" and save 1st part
	return str(pubScore[0])

def printMatrix(matrixP):		#fancy matrices renderer for debugging
	for row in matrixP:
	    for val in row:
	        print '{:4}'.format(val),
	    print

def flattenGarden():		#using only in csv logs, shaping fancy flatten Garden
	s = "["
	for row in Garden:
		for val in row:
			s = s + str(val) + " "
		s = s + "- "
	s = s[:(len(s)-3)] + "]"
	return s

#find all page elements with class-name "tile" and parse it class-names, make matrix from this data and show it 
def growth(gardenG):
	global Garden
	Garden = np.zeros((4, 4), dtype=np.int)
	for i in gardenG:
		mes = re.findall(r"\d+", str(i.get_attribute("class")))		#take only digits from class-name
		Garden[(int(mes[2])-1), (int(mes[1])-1)] = int(mes[0])		#put it to the 2D matrix
	#print "Garden:"
	#printMatrix(Garden)

def zeroRemove(lineZ):		#deleting all zeroes from list
	for k in range(0, 3):
		for i in range(0, 3):
			if lineZ[i] == 0 and lineZ[i+1] != 0:
				x = lineZ[i+1]
				lineZ[i] = x
				lineZ[i+1] = 0
	return lineZ

def powerPerform(lineP):	#make tile multiplication
	global InternalScore
	for i in range(0, 3):
		if lineP[i] == lineP[i+1]:
			y = lineP[i]*2
			InternalScore = InternalScore + y 		#score it
			lineP[i] = y
			lineP[i+1] = 0
	return lineP

def lineAction(lineL):		#perform turn-simulation on exact column
	if len(set(lineL)) == 1:	#if all elements is identical
		x = lineL[0]*2
		lineL = [x, x, 0, 0]
	else:
		lineL = zeroRemove(lineL) 
		lineL = powerPerform(lineL)
		lineL = zeroRemove(lineL)	#need to remove new zeroes after multiplication
	return lineL
"""
def neighborsCheck(matrixN):
    flatN = np.zeros((4, 4), dtype=np.int)
    nScore = 0
    d = 1 													#radius of neighborhood
    i, j = np.where(matrixN == np.amax(matrixN)) 			#get index of max element
    fi = i[0]
    fj = j[0]
    flatN = np.copy(matrixN)
    flatN[fi, fj] = 0
    flatN = np.sort(flatN, axis=None)[::-1]				#1d array of sorted high to low elements except amax value
    if len(flatN) > 8 :
    	flatN = np.resize(flatN, (1, 8))
    flatN = np.all(flatN != 0)
    #np.trim_zeros(flatN)
    #print fi 
    #print fj 
    print "!!!!!!!!!!!!!!!!!!!!!!"
    print flatN
    n = matrixN[fi-d:fi+d+1, fj-d:fj+d+1].flatten()
    n = np.hstack((n[:len(n)//2],n[len(n)//2+1:] ))			# remove the element (fi,fj)
    print n
    for k in flatN :
    	if np.any(n == flatN[k]) :
    		nScore += 1
    return nScore
"""
def perspCount(inputP):
	pCount = 0
	for x in range(0, 4):
		for i in range(0, 3):
			if inputP[i, x] != 0 and inputP[i, x] == inputP[i+1, x] :
				pCount += 1
	for x in range(0, 4):
		for i in range(0, 3):
			if inputP[x, i] != 0 and inputP[x, i] == inputP[x, i+1] :
				pCount += 1
	return pCount

def cornerCount(inputC):
	cornerScore = 0
	max = np.amax(inputC)
	if any([inputC[0, 0] == max, inputC[0, 3] == max, inputC[3, 0] == max, inputC[3, 3] == max]) :
		cornerScore += 2
	return cornerScore

def turnEmul(gardenT, direction):		#4 turn emulation depends on arrow direction
	global InternalScore
	InternalScore = 0
	outputT = np.zeros((4, 4), dtype=np.int)
	if direction == "right":
		gardenT = np.rot90(gardenT, 3)		#rotate matrix CCW x3 for right arrow turn
	elif direction == "up":
		gardenT = np.rot90(gardenT, 2)
	elif direction == "left":
		gardenT = np.rot90(gardenT, 1)
	for i in range(0, 4):
		originT = [gardenT[3, i], gardenT[2, i], gardenT[1, i], gardenT[0, i]]		#map garden column to operation list
		tempT = lineAction(originT)
		tempT = tempT[::-1]		#reverse list
		for k in range(0, 4):
			outputT[k, i] = tempT[k]		#fill each column to outputT matrix
	#perspScore = perspCount(outputT)		#check intendation
	#cornerScore = cornerCount(outputT)
	#neighborScore = neighborsCheck(outputT)
	if direction == "right":
		outputT = np.rot90(outputT, 1)	#rotate matrix CCW back to input state
	elif direction == "up":
		outputT = np.rot90(outputT, 2)
	elif direction == "left":
		outputT = np.rot90(outputT, 3)
	scoreT = InternalScore
	perspScore = perspCount(outputT)	
	cornerScore = cornerCount(outputT)
	#neighborScore = neighborsCheck(outputT)
	print "Emulated" + "-" + direction + ":"
	printMatrix(outputT)
	print perspScore, cornerScore#, neighborScore
	return outputT, scoreT, perspScore, cornerScore#, neighborScore		#this will return tuple!

def weightLifter(matrixW):		#taken DRUL matrix with values and compile list with turns priority on output
	for x in range(0, 4):
		matrixW[0, x] = 16 - matrixW[0, x]		#convert count of non-zeros into  zeros
	k = np.sum(matrixW, axis=0)
	tup = sorted([('down', k[0, 0]), ('right', k[0, 1]), ('up', k[0, 2]), ('left', k[0, 3])], key=lambda x: x[1])[::-1]			#list of tuples sorted by scores and inverted from max to min
	#printMatrix(Garden)
	return tup

def decisionMaker(gardenD):
	global CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft, ScoreCheck, CounterGames
	downMatrix, downScore, downPersp, downCorSore = turnEmul(Garden, "down")		#unpack returned tuple of matrix and int score
	rightMatrix, rightScore, rightPersp, rightCorScore = turnEmul(Garden, "right")
	upMatrix, upScore, upPersp, upCorScore = turnEmul(Garden, "up")
	leftMatrix, leftScore, leftPersp, leftCorScore = turnEmul(Garden, "left")					
	map = {'down':downMatrix, 'right':rightMatrix, 'up':upMatrix, 'left':leftMatrix}
	drul = np.matrix([(np.count_nonzero(downMatrix), np.count_nonzero(rightMatrix), np.count_nonzero(upMatrix), np.count_nonzero(leftMatrix)),
					(downScore, rightScore, upScore, leftScore),
					(downPersp, rightPersp, upPersp, leftPersp),
					(downCorSore, rightCorScore, upCorScore, leftCorScore),
					#(downNeiScore, rightNeiScore, upNeiScore, leftNeiScore),
					(0, 0, 0, 0)])
	tuplist = weightLifter(drul)
	print tuplist
	if np.array_equal(Garden, map[tuplist[0][0]]) == False :
		decision = tuplist[0][0]
	elif np.array_equal(Garden, map[tuplist[1][0]]) == False :
		decision = tuplist[1][0]
	elif np.array_equal(Garden, map[tuplist[2][0]]) == False :
		decision = tuplist[2][0]
	elif np.array_equal(Garden, map[tuplist[3][0]]) == False :
		decision = tuplist[3][0]
	else :
		gameTimer("stop")
		logToFile()
		printSummary()

		time.sleep(0.5)
		TimerStart, TimerStop = 0, 0
		CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft = 0, 0, 0, 0, 0
		InternalScore, ScoreCheck = 0, 0
		retryBtn = driver.find_element_by_class_name("retry-button")
		retryBtn.click()
		CounterGames -= 1
		if CounterGames <= 0 :
			driver.close()
			sys.exit()
		else:
			time.sleep(2)
			return None

	if decision == "down":
		CounterTurnDown += 1 		#increment variable
		ScoreCheck = ScoreCheck + downScore
	if decision == "right":
		CounterTurnRight += 1
		ScoreCheck = ScoreCheck + rightScore
	if decision == "up":
		CounterTurnUp += 1
		ScoreCheck = ScoreCheck + upScore
	if decision == "left":
		CounterTurnLeft += 1
		ScoreCheck = ScoreCheck + leftScore
	CounterTurn += 1
	print decision.upper()
	return decision

while args.debug == True:
	quit = ["stop", "exit", "quit", "q"]
	action = ["action", "act"]
	play = ["play", "pl"]
	response = raw_input()
	if response in action:
		#print ArgDict
		print args.games
	elif response in play:
		element = driver.find_element_by_tag_name("body")
		gameTimer("start")
		while True:
			seeds = driver.find_elements_by_class_name("tile")
			growth(seeds)
			d = decisionMaker(Garden)
			if d == "down":
				element.send_keys(Keys.ARROW_DOWN)
			elif d == "right":
				element.send_keys(Keys.ARROW_RIGHT)
			elif d == "up":
				element.send_keys(Keys.ARROW_UP)
			elif d == "left":
				element.send_keys(Keys.ARROW_LEFT)
			time.sleep(0.1)
	elif response in quit:
		time.sleep(0.1)
		driver.close()
		sys.exit()

while args.play == True:
	element = driver.find_element_by_tag_name("body")      
	with open ("without-animation.js", "r") as myfile :
		data = myfile.read().replace('\n', '')
	driver.execute_script(data)
	"""driver.execute_script(
		"var css = document.createElement(\"style\");" +
		"css.type = \"text/css\";" +
		"css.innerHTML = \".tile { -webkit-transition : none !important; transition : none !important; } .tile-merged .tile-inner { -webkit-animation : none !important; animation : none !important; } .tile-new .tile-inner { -webkit-animation : none !important; animation : none !important; }\";" +
		"document.body.appendChild(css);" 
		#"$tile.addClass(\"notransition\");" +
		#"$tile-new.addClass(\"noanimation\");" +
		#"$tile-merged.addClass(\"noanimation\");"
		)"""
	gameTimer("start")
	while True:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		d = decisionMaker(Garden)
		if d == "down":
			element.send_keys(Keys.ARROW_DOWN)
		elif d == "right":
			element.send_keys(Keys.ARROW_RIGHT)
		elif d == "up":
			element.send_keys(Keys.ARROW_UP)
		elif d == "left":
			element.send_keys(Keys.ARROW_LEFT)
		time.sleep(0.1)





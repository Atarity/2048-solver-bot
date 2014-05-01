import os, time, re, sys, csv, datetime, itertools, timeit
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chromedriver = "/Users/user/Downloads/chromedriver"		#tricky part depends on bug in Python/Selenium, SO it
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

driver.get("http://gabrielecirulli.github.io/2048/")
assert "2048" in driver.title

Version = "0.0.6"
Garden = np.zeros((4, 4), dtype=np.int)		#global matrix for storing tiles state
TimerStart, TimerStop = 0, 0
CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft = 0, 0, 0, 0, 0

def gameTimer(standbyG):		#game stopwatch
	global TimerStart, TimerStop
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
	    		max(itertools.chain(*Garden)), 
	    		gameTimer("show"), 										#time spent
	    		round(CounterTurn / float(gameTimer("tps")), 2),		#turns per secons
	    		CounterTurn, 											#turns total
	    		round(float(CounterTurnDown) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnRight) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnUp) / CounterTurn * 100, 1), 
	    		round(float(CounterTurnLeft) / CounterTurn * 100, 1), 
	    		Garden.flatten('C')]
	    a.writerow(data)

def printSummary():		#print summary after game finished
	print " "
	printMatrix(Garden)
	print " "
	print "Score:         " + getPubScore()
	print "MaxTile:       " + str(max(itertools.chain(*Garden)))		#flatten Garden and found max tile
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
	for i in range(0, 3):
		if lineP[i] == lineP[i+1]:
			y = lineP[i]*2
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

def turnEmul(gardenT, direction):		#4 turn emulation depends on arrow direction
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
			outputT[k, i] = tempT[k]
	if direction == "right":
		outputT = np.rot90(outputT, 1)	#rotate matrix CCW back to input state
	elif direction == "up":
		outputT = np.rot90(outputT, 2)
	elif direction == "left":
		outputT = np.rot90(outputT, 3)
	#print "Emulated" + "-" + direction + ":"
	#printMatrix(outputT)
	return outputT
	#return np.asmatrix(outputT)

def decisionMaker(gardenD):
	global CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft
	downMatrix = turnEmul(Garden, "down")
	rightMatrix = turnEmul(Garden, "right")
	upMatrix = turnEmul(Garden, "up")
	leftMatrix = turnEmul(Garden, "left")
	d = np.count_nonzero(downMatrix)		#count all non-zero entries if turn arrow-down
	r = np.count_nonzero(rightMatrix)	
	u = np.count_nonzero(upMatrix)	
	l = np.count_nonzero(leftMatrix)	
	listD = [d, r, u, l]
	#print listD
	if any( [np.array_equal(Garden, downMatrix) == True, np.array_equal(Garden, rightMatrix) == True, np.array_equal(Garden, upMatrix) == True, np.array_equal(Garden, leftMatrix) == True] ):
		if np.array_equal(Garden, downMatrix) == False :
			decision = "down"
		elif np.array_equal(Garden, rightMatrix) == False :
			decision = "right"
		elif np.array_equal(Garden, upMatrix) == False :
			decision = "up"
		elif np.array_equal(Garden, leftMatrix) == False :
			decision = "left"
		else:
			gameTimer("stop")
			logToFile()
			printSummary()
			driver.close()
			sys.exit()
	else:
		if listD.index(min(listD)) == 0:		#the decision depends on how many non-zero tiles in predicted garden
			decision = "down"
		elif listD.index(min(listD)) == 1:
			decision = "right"
		elif listD.index(min(listD)) == 2:
			decision = "up"
		elif listD.index(min(listD)) == 3:
			decision = "left"	
	if decision == "down":
		CounterTurnDown += 1 		#increment variable
	if decision == "right":
		CounterTurnRight += 1
	if decision == "up":
		CounterTurnUp += 1
	if decision == "left":
		CounterTurnLeft += 1
	CounterTurn += 1
	return decision

while True:
	grid = ["grid", "growth", "g"]
	quit = ["stop", "exit", "quit", "q"]
	action = ["action", "act"]
	play = ["play", "pl"]
	down = ["down", "dwn"]
	right = ["right", "rt"]
	up = ["up"]
	left = ["left", "lt"]
	response = raw_input()
	if response in grid:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
	elif response in action:
		gameTimer("start")
		time.sleep(5)
		gameTimer("stop")
		print gameTimer("show")
	elif response in play:
		element = driver.find_element_by_tag_name("body")
		gameTimer("start")
		while True:
			seeds = driver.find_elements_by_class_name("tile")
			growth(seeds)
			d = decisionMaker(Garden)
			print d.upper()
			if d == "down":
				element.send_keys(Keys.ARROW_DOWN)
			elif d == "right":
				element.send_keys(Keys.ARROW_RIGHT)
			elif d == "up":
				element.send_keys(Keys.ARROW_UP)
			elif d == "left":
				element.send_keys(Keys.ARROW_LEFT)
			time.sleep(0.1)
	elif response in down:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		turnEmul(Garden, "down")
	elif response in right:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		turnEmul(Garden, "right")
	elif response in up:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		turnEmul(Garden, "up")
	elif response in left:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		turnEmul(Garden, "left")
	elif response in quit:
		time.sleep(0.1)
		driver.close()
		sys.exit()





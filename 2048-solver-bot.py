import os, time, re, sys, csv, datetime, itertools, timeit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chromedriver = "/Users/user/Downloads/chromedriver"		#tricky part depends on bug in Python/Selenium, SO it
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

driver.get("http://gabrielecirulli.github.io/2048/")
assert "2048" in driver.title

Version = "0.0.4"
Garden = [[0 for _ in range (4)] for _ in range (4)]	#global matrix for storing tiles state
TimerStart = 0 
TimerStop = 0

def gameTimer(standbyG):
	global TimerStart, TimerStop
	if standbyG == "start":
		TimerStart = timeit.default_timer()
	elif standbyG == "stop":
		TimerStop = timeit.default_timer()
	else:
		overall = TimerStop - TimerStart
		return time.strftime('%M:%S', time.localtime(overall))

def logToFile():
	with open('ResultLog.csv', 'a',) as fp:		#write results to the file
	    a = csv.writer(fp, delimiter=',')
	    data = [Version, datetime.datetime.now().strftime("%d%B%Y %H:%M:%S"), getPubScore(), max(itertools.chain(*Garden)), gameTimer("show")]
	    a.writerow(data)

def getPubScore():		#get game score
	score = driver.find_element_by_class_name("score-container")
	pubScore = eval(score.get_attribute("innerText"))		#remove eval(), use re
	return str(pubScore)

def printMatrix(matrixP):
	for row in matrixP:
	    for val in row:
	        print '{:4}'.format(val),
	    print

#find all page elements with class-name "tile" and parse it class-names, make matrix from this data and show it 
def growth(gardenG):
	global Garden
	Garden = [[0 for _ in range (4)] for _ in range (4)]
	for i in gardenG:
		mes = re.findall(r"\d+", str(i.get_attribute("class")))		#take only digits from class-name
		Garden[int(mes[2])-1][int(mes[1])-1] = int(mes[0])		#put it to the 2D matrix
	print "Garden:"
	printMatrix(Garden)

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
	outputT = [[0 for _ in range (4)] for _ in range (4)]
	if direction == "right":
		gardenT = zip(*gardenT[::-1])		#rotate matrix CW for right arrow turn
	elif direction == "up":
		gardenT = zip(*gardenT[::-1])
		gardenT = zip(*gardenT[::-1])		#rotate it twice
	elif direction == "left":
		gardenT = zip(*gardenT)[::-1]
	for i in range(0, 4):
		originT = [gardenT[3][i], gardenT[2][i], gardenT[1][i], gardenT[0][i]]		#map garden column to operation list
		tempT = lineAction(originT)
		tempT = tempT[::-1]		#reverse list
		for k in range(0, 4):
			outputT[k][i] = tempT[k]
	if direction == "right":
		outputT = zip(*outputT)[::-1]	#rotate matrix CCW back to input state
	elif direction == "up":
		outputT = zip(*outputT)[::-1]
		outputT = zip(*outputT)[::-1]
	elif direction == "left":
		outputT = zip(*outputT[::-1])
	print "Emulated" + "-" + direction + ":"
	printMatrix(outputT)
	return map(list, outputT)		#fixing data structures, remove list of tuples in output

def decisionMaker(gardenD):
	downMatrix = turnEmul(Garden, "down")
	rightMatrix = turnEmul(Garden, "right")
	upMatrix = turnEmul(Garden, "up")
	leftMatrix = turnEmul(Garden, "left")
	d = sum(sum(1 for i in row if i) for row in downMatrix)		#count all non-zero entries if turn arrow-down
	r = sum(sum(1 for i in row if i) for row in rightMatrix)	
	u = sum(sum(1 for i in row if i) for row in upMatrix)	
	l = sum(sum(1 for i in row if i) for row in leftMatrix)	
	listD = [d, r, u, l]
	print listD
	if any( [Garden == downMatrix, Garden == rightMatrix, Garden == upMatrix, Garden == leftMatrix] ):
		if Garden != downMatrix :
			decision = "down"
		elif Garden != rightMatrix :
			decision = "right"
		elif Garden != upMatrix :
			decision = "up"
		elif Garden != leftMatrix :
			decision = "left"
		else:
			gameTimer("stop")
			logToFile()
			print "Score: " + getPubScore()
			print "MaxTile: " + str(max(itertools.chain(*Garden)))		#flatten Garden and found max tile
			print "Time spent (m:s) : " + gameTimer("show")
			print "Where is no way to solve it! Or it already solved.)"
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
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
		print decisionMaker(Garden)
		time.sleep(3)
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





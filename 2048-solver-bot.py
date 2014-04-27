import os, time, re, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chromedriver = "/Users/user/Downloads/chromedriver"		#tricky part depends on bug in Python/Selenium, SO it
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

driver.get("http://gabrielecirulli.github.io/2048/")
assert "2048" in driver.title

Garden = [[0 for _ in range (4)] for _ in range (4)]	#global matrix for storing tiles state

#find all page elements with class-name "tile" and parse it class-names, make matrix from this data and show it 
def growth(gardenG):
	global Garden
	Garden = [[0 for _ in range (4)] for _ in range (4)]
	print "Garden:"
	for i in gardenG:
		mes = re.findall(r"\d+", str(i.get_attribute("class")))		#take only digits
		Garden[int(mes[2])-1][int(mes[1])-1] = int(mes[0])		#put it to the 2D matrix
		#print mes
	for row in Garden:
	    for val in row:
	        print '{:4}'.format(val),
	    print

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

def lineAction(lineL):
	if len(set(lineL)) == 1:	#if all elements is identical
		x = lineL[0]*2
		lineL = [x, x, 0, 0]
	else:
		lineL = zeroRemove(lineL) 
		lineL = powerPerform(lineL)
		lineL = zeroRemove(lineL)	#need to remove new zeroes after multiplication
	return lineL

def turnEmul(gardenT, direction):
	outputT = [[0 for _ in range (4)] for _ in range (4)]
	if direction == "right":
		gardenT = zip(*gardenT[::-1])		#rotate matrix CW for right arrow turn
	elif direction == "up":
		gardenT = zip(*gardenT[::-1])
		gardenT = zip(*gardenT[::-1])		#rotate it twice
	if direction == "left":
		gardenT = zip(*gardenT)[::-1]
	for i in range(0, 4):
		originT = [gardenT[3][i], gardenT[2][i], gardenT[1][i], gardenT[0][i]]		#map garden column to operation list
		tempT = lineAction(originT)
		tempT = tempT[::-1]		#reverse list
		for k in range(0, 4):
			outputT[k][i] = tempT[k]
	if direction == "right":
		outputT = zip(*outputT)[::-1]	#rotate matrix CCW back to input state
	if direction == "up":
		outputT = zip(*outputT)[::-1]
		outputT = zip(*outputT)[::-1]
	if direction == "left":
		outputT = zip(*outputT[::-1])
	print "Emulated" + "-" + direction + ":"
	for row in outputT:
	    for val in row:
	        print '{:4}'.format(val),
	    print

"""element = driver.find_element_by_tag_name("body")
element.send_keys(Keys.ARROW_DOWN)
time.sleep(0.1)
element.send_keys(Keys.ARROW_LEFT)
time.sleep(0.1)
element.send_keys(Keys.ARROW_UP)
time.sleep(0.1)
element.send_keys(Keys.ARROW_RIGHT)"""
while True:
	grid = ["grid", "growth", "g"]
	quit = ["stop", "exit", "quit", "q"]
	action = ["action", "act"]
	down = ["down", "dwn"]
	right = ["right", "rt"]
	up = ["up"]
	left = ["left", "lt"]
	response = raw_input()
	if response in grid:
		seeds = driver.find_elements_by_class_name("tile")
		growth(seeds)
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





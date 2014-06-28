# -*- coding: utf-8 -*-

import os, time, re, sys, csv, datetime, timeit, argparse, gc, codecs
import numpy as np
import itertools
from operator import itemgetter
from pushbullet import Device
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import snake

class gamesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values <= 0 or values > 1000:
            parser.error("Games to play number should be in range 1..1000")
        setattr(namespace, self.dest, values)


class modsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < -1000 or values > 1000:
            parser.error("Modificator value should be in range -1000..1000")
        setattr(namespace, self.dest, values)


class noteAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, basestring) == False:
            parser.error("Please, use quotes \" \" to determine you note as argument")
        if len(values) > 140:
            parser.error("Too long note. Make it Twitter-way with no longer than 140 chars")
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(
    description="This bot will try to solve 2048 puzzle game which hosted on http://gabrielecirulli.github.io/2048/")
parser.add_argument("-p", "--play", help="immediately starts playing", action="store_true")
parser.add_argument("-a", "--noanim", help="remove tile animation to speed up process", action="store_true")
parser.add_argument("-g", "--games", help="play exact X games", action=gamesAction, metavar="X", type=int, default=1)
parser.add_argument("-n", "--note",
                    help="short note string (<140chrs) in \"quotes\" will add to csv with each game result",
                    action=noteAction, metavar="STR", type=str, default="")
parser.add_argument("-d", "--debug", help="reserved for debugging purposes", action="store_true")
parser.add_argument("-l", "--loglevel", help="verbose level from 0 to 2", choices=range(0, 3), metavar="X", type=int,
                    default=1)
parser.add_argument("-ph", "--phantom", help="run Selenium in headless mode with PhantomJS", action="store_true")
parser.add_argument("-pb", "--push", help="turn on PushBullet notifications with top results", action="store_true")
parser.add_argument("-me", "--emptymod", help="\"Empty\" modificator value", action=modsAction, metavar="X", type=float,
                    default=1)
parser.add_argument("-ms", "--scoremod", help="\"Score\" modificator value", action=modsAction, metavar="X", type=float,
                    default=1)
parser.add_argument("-mc", "--cornermod", help="\"Corner\" modificator value", action=modsAction, metavar="X", type=float,
                    default=0)
parser.add_argument("-mp", "--perspmod", help="\"Perspective\" modificator value", action=modsAction, metavar="X",
                    type=float, default=1)
parser.add_argument("-mr", "--perfmod", help="\"Perfect snake\" modificator value", action=modsAction, metavar="X",
                    type=float, default=1)
args = parser.parse_args()
ArgDict = vars(args)  #used for debugging only


Version = "0.1.9"
Garden = np.zeros((4, 4), dtype=np.int)  #global matrix for storing tiles state
TimerStart, TimerStop = 0, 0
CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft = 0, 0, 0, 0, 0
InternalScore, ScoreCheck = 0, 0
EmptyMod, ScoreMod, CornerMod, PerspMod, PerfectMod = args.emptymod, args.scoremod, args.cornermod, args.perspmod, args.perfmod
CounterGames = args.games
Note = str(args.note).replace(",", " ").rstrip('\n')  #force remove all commas from notes and \n
KeepGoing = False                                       #is 2048 tile reached and game continued?
Driver, Element = None, None

#--------------------------------
#This section is about platform- and user- dependant settings. Use your own Pushbullet API key and use your own platform paths to phantomJS and Chromedriver
#--------------------------------
PB_api_key = "v1mJDwghGTdeyPxxnToKBZ1qAYIUx83sKFujwVbgDhJ5o"    #Your own PushBullet API key
phone = Device(PB_api_key, "5685265389584384")                  #Your own Pushbullet device ID


def loadNewGame():
    global Driver, Element, TimerStart, TimerStop, CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft, InternalScore, ScoreCheck, KeepGoing
    TimerStart, TimerStop = 0, 0
    CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft = 0, 0, 0, 0, 0
    InternalScore, ScoreCheck = 0, 0
    KeepGoing = False
    if args.phantom == True :
        driverPath = "D:\phantomjs197\phantomjs.exe"                #WIN for PhantomJS
        Driver = webdriver.PhantomJS(driverPath)            
    else :
        #driverPath = "/Users/user/Downloads/chromedriver"          #OS X for Chromedriver
        driverPath = "D:\chromedriver.exe"                          #WIN fro Chromedriver
        os.environ["webdriver.chrome.driver"] = driverPath
        Driver = webdriver.Chrome(driverPath)
    Driver.delete_all_cookies()
    Driver.get("http://gabrielecirulli.github.io/2048/")
    assert "2048" in Driver.title
    if args.phantom == True :                                       #PHJS workaround (cache clearing issue)
        restartBtn = Driver.find_element_by_class_name("restart-button")
        restartBtn.click()
    if args.play == True :
        Element = Driver.find_element_by_tag_name("body")
        if args.noanim == True :                             #run script thru selenium if user turn off tile animation
            with open("without-animation.js", "r") as myfile:
                data = myfile.read().replace('\n', '')
            Driver.execute_script(data)
        gameTimer("start")
#--------------------------------
#End of platform- and user- dependant settings.
#--------------------------------


def gameTimer(standbyG):  #game stopwatch
    global TimerStart, TimerStop
    overall = 0
    if standbyG == "start":
        TimerStart = timeit.default_timer()
    elif standbyG == "stop":
        TimerStop = timeit.default_timer()
    elif standbyG == "tps":
        overall = TimerStop - TimerStart
        t = time.strftime('%M:%S', time.localtime(overall))
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(t.split(":"))))  #manually convert to total seconds
    elif standbyG == "show":
        overall = TimerStop - TimerStart
        return time.strftime('%M:%S', time.localtime(overall))


def logToFile():
    global CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft, Garden, Note, Version
    with codecs.open("ResultLog.csv", "ab", "UTF-8") as fp:  #write results to the file
        a = csv.writer(fp, delimiter=',')
        data = [Version,
                datetime.datetime.now().strftime("%d%B%Y %H:%M:%S"),
                getPubScore(),
                np.amax(Garden),                                        #max tile
                gameTimer("show"),                                      #time spent
                round(CounterTurn / float(gameTimer("tps")), 2),  #turns per secons
                CounterTurn,                                        #turns total
                round(float(CounterTurnDown) / CounterTurn * 100, 1),
                round(float(CounterTurnRight) / CounterTurn * 100, 1),
                round(float(CounterTurnUp) / CounterTurn * 100, 1),
                round(float(CounterTurnLeft) / CounterTurn * 100, 1),
                flattenGarden(),
                Note]
        a.writerow(data)


def printSummary():  #print summary after game finished
    global ScoreCheck, Garden, CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft
    print " "
    printMatrix(Garden)
    print " "
    print "Score:         " + str(getPubScore())
    print "Score check:   " + str(ScoreCheck)
    print "MaxTile:       " + str(np.amax(Garden))  #flatten Garden and found max tile
    print "Turns total:   " + str(CounterTurn)
    print "       down:   " + str(round(float(CounterTurnDown) / CounterTurn * 100, 1)) + "%"
    print "      right:   " + str(round(float(CounterTurnRight) / CounterTurn * 100, 1)) + "%"
    print "         up:   " + str(round(float(CounterTurnUp) / CounterTurn * 100, 1)) + "%"
    print "       left:   " + str(round(float(CounterTurnLeft) / CounterTurn * 100, 1)) + "%"
    print "Time (m:s):    " + gameTimer("show")
    print "Turns per sec: " + str(round(CounterTurn / float(gameTimer("tps")), 2))
    print " "


def getPubScore():                  #get game score directly from web page
    score = Driver.find_element_by_class_name("score-container")
    pubScore = re.split('\+', score.get_attribute("innerText"))  #split string on "+" and save 1st part
    return int(pubScore[0])


def getMaxFromFile():               #get all time maximum score from resultlog.csv
    scoreList = []
    with codecs.open("ResultLog.csv", "rb", "UTF-8") as fp:
        a = csv.reader(fp, delimiter = ",")
        for row in a :
            scoreList.append(row[2])
        scoreList.remove("Score")        
        return np.amax(np.asarray(scoreList).astype(int))               #turn list into np array, convert to int and return max element


def printMatrix(matrixP):  #fancy matrices renderer for debugging
    for row in matrixP:
        for val in row:
            print '{:4}'.format(val),
        print


def flattenGarden():  #using only in csv logs, shaping fancy flatten Garden
    s = "["
    for row in Garden:
        for val in row:
            s = s + str(val) + " "
        s = s + "- "
    s = s[:(len(s) - 3)] + "]"
    return s


def growth(gardenG):                #find all page elements with class-name "tile" and parse it class-names, make matrix from this data and show it
    global Garden
    Garden = np.zeros((4, 4), dtype=np.int)
    for i in gardenG:
        mes = re.findall(r"\d+", str(i.get_attribute("class")))  #take only digits from class-name
        Garden[(int(mes[2]) - 1), (int(mes[1]) - 1)] = int(mes[0])  #put it to the 2D matrix
    if args.loglevel > 0:
        if args.loglevel > 1:
            print "Garden:"
            printMatrix(Garden)


def zeroRemove(lineZ):  #deleting all zeroes from list
    for k in range(0, 3):
        for i in range(0, 3):
            if lineZ[i] == 0 and lineZ[i + 1] != 0:
                x = lineZ[i + 1]
                lineZ[i] = x
                lineZ[i + 1] = 0
    return lineZ


def powerPerform(lineP):  #make tile multiplication
    global InternalScore
    for i in range(0, 3):
        if lineP[i] == lineP[i + 1]:
            y = lineP[i] * 2
            InternalScore += y          #score it
            lineP[i] = y
            lineP[i + 1] = 0
    return lineP


def lineAction(lineL):              #perform turn-simulation on exact column
    if len(set(lineL)) == 1:        #if all elements is identical
        x = lineL[0] * 2
        lineL = [x, x, 0, 0]
    else:
        lineL = zeroRemove(lineL)
        lineL = powerPerform(lineL)
        lineL = zeroRemove(lineL)  #need to remove new zeroes after multiplication
    return lineL


def perspCount(inputP):
    pCount = 0
    for x in range(0, 4):
        for i in range(0, 3):
            if inputP[i, x] != 0 and inputP[i, x] == inputP[i + 1, x]:
                pCount += inputP[i, x]  #increase perp score by tile value
    for x in range(0, 4):
        for i in range(0, 3):
            if inputP[x, i] != 0 and inputP[x, i] == inputP[x, i + 1]:
                pCount += inputP[x, i]
    return pCount * 2


def cornerCount(inputC):            #got scores if max garden tile are in one of the corner
    cornerScore = 0
    max = np.amax(inputC)
    if any([inputC[0, 0] == max, inputC[0, 3] == max, inputC[3, 0] == max, inputC[3, 3] == max]):
        cornerScore += (max / 4)
    return cornerScore


def getPerfectList(a2d):
    """
    :type a2d: np.ndarray
    :rtype : iterable
    returns perfect-sorted list
    """
    return sorted(snake.SnakeUnfolder(a2d), reverse=True)


def getPerfectDiff(a2d):
    """
    :type a2d: np.ndarray
    :rtype : float
    returns difference between perfect-sorted list (i.e. 2,4,8,4 4,2,8,4)
    """
    pl = getPerfectList(a2d)
    distmap = [i for i in range(0, len(pl))]
    perfScores = reduce(lambda a, (d, (p, l)): a - abs(p-l), zip(distmap, zip(pl, snake.SnakeUnfolder(a2d))), 0)
    return perfScores / float(sum(pl))


def turnEmul(gardenT, direction):       #4 turn emulation depends on arrow direction
    global InternalScore
    InternalScore = 0
    outputT = np.zeros((4, 4), dtype=np.int)
    if direction == "right":
        gardenT = np.rot90(gardenT, 3)  #rotate matrix CCW x3 for right arrow turn
    elif direction == "up":
        gardenT = np.rot90(gardenT, 2)
    elif direction == "left":
        gardenT = np.rot90(gardenT, 1)
    for i in range(0, 4):
        originT = [gardenT[3, i], gardenT[2, i], gardenT[1, i], gardenT[0, i]]  #map garden column to operation list
        tempT = lineAction(originT)
        tempT = tempT[::-1]  #reverse list
        for k in range(0, 4):
            outputT[k, i] = tempT[k]  #fill each column to outputT matrix
    if direction == "right":
        outputT = np.rot90(outputT, 1)  #rotate matrix CCW back to input state
    elif direction == "up":
        outputT = np.rot90(outputT, 2)
    elif direction == "left":
        outputT = np.rot90(outputT, 3)
    scoreT = InternalScore
    perspScore = 0 if np.array_equal(gardenT, outputT) else perspCount(outputT)
    cornerScore = cornerCount(outputT)
    filledBefore = np.count_nonzero(gardenT)
    filledAfter = np.count_nonzero(outputT)
    zerosScore = filledBefore - filledAfter
    perfectnessScore = getPerfectDiff(outputT)
    if args.loglevel > 0:
        if args.loglevel > 1:
            print "Emulated" + "-" + direction + ":"
            printMatrix(outputT)
            print "Zeros: " + str(zerosScore) + " Score: " + str(scoreT) + " Persp: " + str(
                perspScore) + " Corner: " + str(cornerScore)  #, neighborScore
            print " "
    return outputT, zerosScore, scoreT, perspScore, cornerScore, perfectnessScore  #this will return tuple!


#					DRUL matrix cols reperesentes emulated turns: Down, Right, Up, Left and rows is criteria scores
#Number of zeroes tiles after turn (< is better)
#Turn score
#Perspective (after-turn analysis) scores
#Corner scores
#Perfect snake scores
def weightLifter(freespace, matrixW):  #taken DRUL matrix with values and compile list with turns priority on output
    global EmptyMod, ScoreMod, PerspMod, CornerMod, PerfectMod
    for x in range(0, 4):
        matrixW[0, x] = matrixW[0, x] * EmptyMod * ( (16 - freespace) / (freespace + 0.1) if freespace < 4 else 1 )
        matrixW[1, x] *= ScoreMod                                       #apply ScoreMod to score row
        matrixW[2, x] *= PerspMod
        matrixW[3, x] *= CornerMod
        matrixW[4, x] *= PerfectMod
    k = np.sum(matrixW, axis=0)
    tup = sorted([('down', k[0, 0]), ('right', k[0, 1]), ('up', k[0, 2]), ('left', k[0, 3])], key=lambda x: x[1])[
          ::-1]  #list of tuples sorted by scores and inverted from max to min
    if args.loglevel > 0:
        if args.loglevel > 1:
            print "weightLifter output: "
            printMatrix(np.asarray(matrixW))
            print " "
    return tup


def normalize(a,b,c,d,by):          #normalize scores by maximum value
    if by > 0 :
        a /= float(by)
        b /= float(by)
        c /= float(by)
        d /= float(by)
    return a,b,c,d


def decisionMaker(gardenD):
    global CounterTurn, CounterTurnDown, CounterTurnRight, CounterTurnUp, CounterTurnLeft, ScoreCheck, CounterGames, KeepGoing, TimerStart, TimerStop

    if np.amax(gardenD) == 2048 and KeepGoing == False :
        time.sleep(3)
        kpbtn = Driver.find_element_by_class_name("keep-playing-button")
        kpbtn.click()
        KeepGoing = True
        time.sleep(1)

    downMatrix, downZeros, downScore, downPersp, downCorSore, downPerfect = turnEmul(Garden, "down")  #unpack returned tuple of matrix and int score
    rightMatrix, rightZeros, rightScore, rightPersp, rightCorScore, rightPerfect = turnEmul(Garden, "right")
    upMatrix, upZeros, upScore, upPersp, upCorScore, upPerfect = turnEmul(Garden, "up")
    leftMatrix, leftZeros, leftScore, leftPersp, leftCorScore, leftPerfect = turnEmul(Garden, "left")

    zerosMax = max(downZeros, rightZeros, upZeros, leftZeros)
    downZeros, rightZeros, upZeros, leftZeros = normalize(downZeros, rightZeros, upZeros, leftZeros, zerosMax)

    dScore, rScore, uScore, lScore = downScore, rightScore, upScore, leftScore                              # backup scores before normalizing
    scoreMax = max(downScore, rightScore, upScore, leftScore)
    downScore, rightScore, upScore, leftScore = normalize(downScore, rightScore, upScore, leftScore, scoreMax)

    perspMax = max(downPersp, rightPersp, upPersp, leftPersp)
    downPersp, rightPersp, upPersp, leftPersp = normalize(downPersp, rightPersp, upPersp, leftPersp, perspMax)

    map = {"down": downMatrix, "right": rightMatrix, "up": upMatrix, "left": leftMatrix}
    drul = np.matrix([(downZeros, rightZeros, upZeros, leftZeros),
                      (downScore, rightScore, upScore, leftScore),
                      (downPersp, rightPersp, upPersp, leftPersp),
                      (downCorSore, rightCorScore, upCorScore, leftCorScore),
                      (downPerfect, rightPerfect, upPerfect, leftPerfect),
                      (-1000, 0, 0, 0)])
    tuplist = weightLifter(16 - np.count_nonzero(Garden), drul)

    if args.loglevel > 0:
        if args.loglevel > 1:
            print tuplist
        else:                           #loglevel = 1
            for x in range(0, 4):
                print "{:4}".format(str(tuplist[x][0]) + ": " + str(tuplist[x][1])),
            print

    if np.array_equal(Garden, map[tuplist[0][0]]) == False:
        decision = tuplist[0][0]
    elif np.array_equal(Garden, map[tuplist[1][0]]) == False:
        decision = tuplist[1][0]
    elif np.array_equal(Garden, map[tuplist[2][0]]) == False:
        decision = tuplist[2][0]
    elif np.array_equal(Garden, map[tuplist[3][0]]) == False:
        decision = tuplist[3][0]
    else:
        pubScore = getPubScore()
        gameTimer("stop")
        if pubScore > getMaxFromFile():
            Driver.save_screenshot("Screenshots/" + str(pubScore) + ".png")
            if args.push == True :
                with open("Screenshots/" + str(pubScore) + ".png") as png:
                    push = phone.push_file(png, u"Completed during " + gameTimer("show") + u" with max tile " + str(np.amax(Garden)) + u" and speed of " + str(round(CounterTurn / float(gameTimer("tps")), 2)) + u" turns per sec.") 
        logToFile()
        printSummary()
        CounterGames -= 1
        gc.collect()
        time.sleep(0.5)

        if CounterGames <= 0:
            Driver.close()
            Driver.quit()
            sys.exit()
        else:
            Driver.close()
            Driver.quit()            
            time.sleep(2)
            loadNewGame()
            return None

    if decision == "down":
        CounterTurnDown += 1
        ScoreCheck += dScore
    elif decision == "right":
        CounterTurnRight += 1
        ScoreCheck += rScore
    elif decision == "up":
        CounterTurnUp += 1
        ScoreCheck += uScore
    elif decision == "left":
        CounterTurnLeft += 1
        ScoreCheck += lScore
    CounterTurn += 1

    if args.loglevel > 0 :
        if args.loglevel > 1 :
            print decision.upper()
    else :
        sys.stdout.write("\rTurn: %d" %CounterTurn) 
        sys.stdout.flush()

    return decision

loadNewGame()

while args.debug == True:               #debug mode with old raw_input() interface
    if args.noanim == True:
        with open("without-animation.js", "r") as myfile:
            data = myfile.read().replace('\n', '')
        Driver.execute_script(data)
    quit = ["stop", "exit", "quit", "q"]
    action = ["action", "act"]
    response = raw_input()
    if response in action:
        Driver.save_screenshot("Screenshots/test.png")
        with open("Screenshots/test.png", "rb") as png:
            push = phone.push_file(png, "str")
    elif response in quit:
        time.sleep(0.1)
        Driver.close()
        Driver.quit()
        sys.exit()


while True:
    seeds = Driver.find_elements_by_class_name("tile")
    growth(seeds)
    d = decisionMaker(Garden)
    if d == "down":
        Element.send_keys(Keys.ARROW_DOWN)
    elif d == "right":
        Element.send_keys(Keys.ARROW_RIGHT)
    elif d == "up":
        Element.send_keys(Keys.ARROW_UP)
    elif d == "left":
        Element.send_keys(Keys.ARROW_LEFT)
    elif d == None :
        time.sleep(0.1)
    time.sleep(0.1)                         #this small every-turn shit keep selenium out of flooding


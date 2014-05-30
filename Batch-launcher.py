import subprocess, argparse, sys

class gamesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 1 or values > 10000:
            parser.error("Games number should be in range 1..10000")
            #raise argparse.ArgumentError("Minimum bandwidth is 12")
        setattr(namespace, self.dest, values)
class instAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 1 or values > 100:
            parser.error("Instances number should be in range 1..100")
            #raise argparse.ArgumentError("Minimum bandwidth is 12")
        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser(description="Batch game launcher for 2048-solver-bot.py")
parser.add_argument("-g", "--games", help="Play exact X games", action=gamesAction, metavar="X", type=int, default=1, required=True)
parser.add_argument("-i", "--instances", help="Run not more than X bot instances", action=instAction, metavar="X", type=int, default=1, required=True)
args = parser.parse_args()

GamesCounter = args.games
MaxInstances = args.instances

"""for x in range (0, 3):
    print "\"" + str(GamesCounter) + " games on " + str(MaxInstances) + " instances" + "\""
"""
if GamesCounter % MaxInstances == 0 :           #mod, 15 % 4 = 3
    for x in range (0, MaxInstances) :
    	subprocess.Popen(["python", "solverbot2048.py", "-p", "-l 0", "-ph", "-pb", "-g " + str(int(round(GamesCounter/MaxInstances))), "-n" + str(GamesCounter) + " games on " + str(MaxInstances) + " instances"])
#    sys.exit()
else :
    subprocess.Popen(["python", "solverbot2048.py", "-p", "-l 0", "-ph", "-pb", "-g " + str(int(round(GamesCounter/MaxInstances)) + (GamesCounter % MaxInstances)), "-n" + str(GamesCounter) + " games on " + str(MaxInstances) + " instances"])
    for x in range (0, MaxInstances - 1) :
        subprocess.Popen(["python", "solverbot2048.py", "-p", "-l 0", "-ph", "-pb", "-g " + str(int(round(GamesCounter/MaxInstances))), "-n" + str(GamesCounter) + " games on " + str(MaxInstances) + " instances"])
#    sys.exit()
#sys.exit()
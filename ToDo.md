###General

- [x] Migrate math to NumPy
- [x] Run solver with args (play, logs, noanimation, run exact games count, job notes, debug)
	- [x] play
- [x] Version log
- [x] Games results logging into csv (ver, date, time, turns, score, max tile, final Garden flatten)
	- [x] ver
- [x] def getScore()
- [x] Internal scoring system for decision maker
- [ ] Spacebar pause + show current game stats
- [x] def printMatrix()
- [x] Turns percentage
- [x] Avoid eval() for proper public scoring
- [x] def printSummary()
- [x] Turns per sec analytics
- [x] Criteria: Numb of identical tiles on one line after turn
- [x] Criteria: Max board tile is in a corner
- [x] Criteria: Max 8 board tiles is in one sector or idealGarden match
- [ ] Unified cosmo credit system based on max turn score
- [x] Loglevel
- [x] Wait until page loading?? OK fuck this shit
- [x] Remove animation to improve speed
- [x] Force close new mobile apps banner
- [x] Coefs thru args
- [x] Batch laucher
	- [x] Run multiple thru subprocess
	- [ ] MOD for GamesCounter
- [ ] Gitignore for PyCharm

###To fix
 - [x] Fix: TPS in multiple games
 - [x] Fix: remove commas from note before csv write
 - [ ] Fix: use unicode for notes
 - [ ] Fix: internal score counter
 - [ ] Fix: Perspective scores should apply only in case bot get real scores on this turn!
 - [x] Refactor: put all Mod to weightLifter, put all scoring to turnEmulator
 - [x] Remove intertools
 - [ ] Batch-launcher notes \n bug
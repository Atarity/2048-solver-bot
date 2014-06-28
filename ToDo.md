###General

- [x] Migrate math to NumPy
- [x] Run solver with args
	- [x] play
	- [x] logs
	- [x] noanimation
	- [x] run exact games count
	- [x] job notes
	- [x] debug
- [x] Version log
- [x] Games results logging into csv
	- [x] ver
	- [x] date
	- [x] time
	- [x] turns
	- [x] score
	- [x] max tile
	- [x] final Garden flatten
- [x] def getScore()
- [x] Internal scoring system for decision maker
- [ ] Spacebar pause
	- [ ] show current game stats
	- [ ] temporary manual handling
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
	- [x] MOD for GamesCounter
- [x] Gitignore for Py
- [ ] More deeper pespective prediction (up to 5 turn minimax)
- [ ] Down turn minimization based on prediction and weight changing
- [x] PhantomJS
	- [x] -ph arg
	- [x] Process indicator
	- [x] Screenshot if result above top
- [x] Pushbullet API
	- [x] Final screenshot notification thru PB
	- [x] If result is the new best of ResultLog.csv -- PB me
	- [x] Turn PB thru args
- [x] Store all OS and User- dependant pref in one section
- [ ] getPubScore output decorator

### Refactoring
- [x] Game constructor

###Investigation
- [ ] RPi deployment with PhantomJS (headless)
- [ ] DO deployment
- [ ] Threading
- [x] Speed decrease at multiple endless run (PhantomJS) (solved)
- [ ] Collect only "new" tiles from board not all of this
- [x] Find-element-by VS xpath speed (failed)

###To fix
 - [x] Fix: TPS in multiple games
 - [x] Fix: remove commas from note before csv write
 - [ ] Fix: use unicode for notes
 - [ ] Fix: internal score counter.
 - [x] Fix: Perspective scores should apply only in case bot get real scores on this turn!
 - [x] Refactor: put all Mod to weightLifter, put all scoring to turnEmulator
 - [x] Remove intertools
 - [x] Fix csv EOL for WIN 
2048 solver bot
---------------

Dependencies:

 - [Python 2.7](http://www.python.org) with [NumPy](http://www.numpy.org/) library
 - [Selenium](https://pypi.python.org/pypi/selenium) with [ChromeDriver](https://code.google.com/p/chromedriver/)

After installing ChromeDriver it needs to determine binaries location in script line:

`chromedriver = "/Users/user/Downloads/chromedriver"`

##ToDo:

 1. ~~Migrate math to NumPy~~
 2. ~~Run solver with args~~ (~~play~~, ~~logs~~, ~~noanimation~~, ~~run exact games count~~, ~~job notes~~, ~~debug~~)
 3. ~~Version log~~
 4. ~~Games results logging into csv~~ (~~ver~~, ~~date~~, ~~time~~, ~~turns~~, ~~score~~, ~~max tile~~, ~~final Garden flatten~~)
 5. ~~def getScore()~~
 6. ~~Internal scoring system for decision maker~~
 7. Spacebar pause + show current game stats
 8. ~~def printMatrix()~~
 9. ~~Turns percentage~~
 10. ~~Avoid eval() for proper public scoring~~
 11. ~~def printSummary()~~
 12. ~~Turns per sec analytics~~
 13. ~~Remove intertools~~
 14. ~~Criteria: Numb of identical tiles on one line after turn~~
 15. ~~Criteria: Max board tile is in a corner~~
 16. Criteria: Max 8 board tiles is in one sector or idealGarden match
 17. Unified cosmo credit system based on max turn score
 18. ~~Loglevel~~
 19. ~~Wait until page loading?? OK fuck this shit~~
 20. ~~Fix: TPS in multiple games~~
 21. ~~Fix: remove commas from note before csv write~~
 22. Fix: use unicode for notes
 23. ~~Remove animation to improve speed~~
 24. ~~Force close new mobile apps banner~~
 25. Fix: internal score counter
 26. Coefs thru args
 27. Stand-alone batch script with instances control and args tuning
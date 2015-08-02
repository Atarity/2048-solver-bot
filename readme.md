2048 solver bot
---------------

*This bot runs thru Selenium and will connect directly to original web-version of 2048 game which host on http://gabrielecirulli.github.io/2048/ . This game will run all it JS's on client side so no need to worry about web-traffic or Gabriel's server loading.)*

<a href="https://instagram.com/p/oDj3zWKxaW/?taken-by=atar1ty"><img src="https://habrastorage.org/files/c19/6a9/7e9/c196a97e939d429b957ef45e698aa787.jpg" width="450"/></a>

###Dependencies

 - [Python 2.7](http://www.python.org) with [NumPy](http://www.numpy.org/) and [Pushbullet](https://github.com/randomchars/pushbullet.py) libraries
 - [Selenium bindings](https://pypi.python.org/pypi/selenium) for Python with [ChromeDriver](https://code.google.com/p/chromedriver/) or [PhantomJS](http://phantomjs.org/)

After installing ChromeDriver it needs to determine binaries location in script like this:

`chromedriver = "/Users/user/Downloads/chromedriver"`

###Usage
* **ResultLog.csv** &mdash; log of all game played 
* **solverbot2048.py** &mdash; the main script which solves

You should to change paths/API key in platform- and user- dependand section of solverbot2048.py

| Arg    | Full         | Description          |
|--------|--------------|----------------------|  
|-h      | --help       | Show help message and exit |  
|-p      | --play       | Immediately starts playing after running |  
|-a      | --noanim     | Remove tile animation to slightly sped up process |
| -g X   | --games X    | Play exact X games |
| -n STR | --note STR   | Short note string <140 chrs in "quotes" will add to csv with each game result |
| -ph    | --phantom    | run Selenium in headless mode with PhantomJS |
| -pb    | --push       | turn on PushBullet notifications with top results |
| -d     | --debug      | Reserved for debugging purposes |
| -l X   | --loglevel X | Verbose level from 0 to 2 |

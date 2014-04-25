import os, time, re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chromedriver = "/Users/user/Downloads/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

driver.get("http://gabrielecirulli.github.io/2048/")
assert "2048" in driver.title

def growth(garden):
	bed = [[0 for _ in range (4)] for _ in range (4)]
	for i in garden:
		mes = re.findall(r"\d+", str(i.get_attribute("class")))
		bed[int(mes[2])-1][int(mes[1])-1] = int(mes[0])
		#print mes
	for row in bed:
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
time.sleep(20)

garden = driver.find_elements_by_class_name("tile")
growth(garden)

#time.sleep(5)
#driver.close()
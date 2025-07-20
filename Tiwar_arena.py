from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from config import Tiwar_pass,Tiwar_user

"""Functions area"""

def sign_in():
    browser.get("http://www.tiwar.net")
    sign_btn = browser.find_element(by=By.LINK_TEXT,value = "Sign In")
    sign_btn.click()
    username_in = browser.find_element(by = By.NAME,value = "login")
    username_in.send_keys(Tiwar_user)
    password_in = browser.find_element(by=By.NAME,value="pass")
    password_in.send_keys(Tiwar_pass)
    sign_f_btn = browser.find_element(by=By.XPATH, value="/html/body/div/div[1]/div[6]/form/div/span/span/input")
    sign_f_btn.click()

def is_element_present(elem):
    try: 
        browser.find_element_by_partial_link_text(elem)
    except NoSuchElementException as e: return False
    return True

def exception_encountered(e):
    browser.refresh()
    time.sleep(2)
    browser.refresh()
    time.sleep(2)
    browser.refresh()
    print(e)
    time.sleep(50)

"""Variables area"""

w = 1
d = 1 
lasttime = 0

"""Chrome webdrive settings"""

option = webdriver.ChromeOptions()
option.add_argument('headless')
ser = Service('C:\Python\Projects\chromedriver.exe')
browser = webdriver.Chrome(service = ser, options = option)

"""this is just a temporay sentence I am writing as a comment
"""


sign_in()  #sign in to the website
print("logged in")
try:
    arena = browser.find_element(by=By.PARTIAL_LINK_TEXT, value = "Arena")
    arena.click()  
except:
    arena = browser.find_element(by=By.PARTIAL_LINK_TEXT, value = "Monsters")
    arena.click()
#find arena and click on it and if there is a monsters event then it is selected
attacks_count = 0
while(True):
    try:
        """time stuff"""
        
        now = datetime.now()
        currentTime = now.strftime("%H:%M:%S")
        
        """************************************"""
        #we have to find the attack button and also check out the current energy and health values
        attackBtn = browser.find_element(by=By.LINK_TEXT, value = "Attack")
        
        health = browser.find_element(by= By.XPATH, value = "/html/body/div/div[1]/div[1]/span[2]/span")
        energyElem = browser.find_element(by = By.XPATH, value="/html/body/div/div[1]/div[1]/span[2]")
        #extracting the data from the topbar element which shows health and energy
        energyElem = energyElem.text
        energy1 = energyElem.split("| ") #this is required because the energy element occurs as a seperate text between spans instead of being an attribute, same for health
        energy = int(energy1[1])
        health = int(health.text) 
        #converted both the string value to int to perform operations
        """*********************************************"""

        if (health > 810 and energy >= 50):  #checking if health and energy are above threshold
            attackBtn.click()
            attacks_count += 1
            print(f"{attacks_count} attacked")
            time.sleep(3)
        #this section will be accessed if health is below 10% or energy is below 50
        else:
            if(health < 1900 ):
                browser.refresh()
                wait = 1900 - health #defining wait time required according to the default health generation speed
                print("sleeping for", wait,"seconds at \t",currentTime)              
                time.sleep(wait)
                browser.refresh()

            elif(energy < 50):
                browser.refresh()
                wait = 50 - energy #defining wait time required according to the observed default energy generation speed
                wait *= 2 #1.2 energy is generated every 2 seconds so we multiply the number so that we can wait 
                print("sleeping for", wait,"seconds at \t",currentTime)
                time.sleep(int(wait))
                browser.refresh() #refreshing the page after sleeping so that we can have new value to work with in the new loop
    
    except Exception as error:
        exception_encountered(error)


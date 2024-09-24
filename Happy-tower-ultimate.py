import threading
from typing import Text
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
from config import HT_user,HT_pass

"""Chrome webdriver stuff"""

option = webdriver.ChromeOptions()
option.add_argument('headless')
option.add_argument('--log-level=3')
ser = Service('C:\\Python\\Projects\\chromedriver.exe')
browser = webdriver.Chrome(service = ser, options = option)
"""********************"""


"""*******************"""
"""Function stuff"""

def main():
    lifted_count = 1
    collected_count = 1
    sold_count = 1
    bought_count = 1

    signin()
    #initially clicks the show floors section to open it up and start the basic loop
    
    while True:
        try:
            if is_element_present_xpath('.//div[@class="tlbr nshd"]/a[@class="tdn"][2]/img[@alt!="@"]') == True:
                icon = browser.find_element(by=By.XPATH,value='.//div[@class="tlbr nshd"]/a[@class="tdn"][2]/img[@alt!="@"]')
                icon.click()
                result = other_actions(bought_count,collected_count,sold_count)
                bought_count = result[0]
                collected_count = result[1]
                sold_count = result[2]
            
            elif (is_element_present("Lift a visitor") == True):
                temp = operate_lift(lifted_count)
                lifted_count = temp
                click_top()

            else:
                claim_quests()
                special_event()
                click_top()
        
        except Exception as error:
            exception(error)


def buy():
    buy_goods = browser.find_element(by=By.LINK_TEXT,value="Buy goods")
    buy_goods.click()


def claim_quests():
    browser.get("http://happytower.mobi/quests")
    while is_element_present("Claim reward!") == True:
        claim = browser.find_element(by=By.PARTIAL_LINK_TEXT,value="Claim reward!")
        claim.click()
        print("Claimed rewards")


def click_top():
    top = browser.find_element(by=By.XPATH,value="/html/body/div/div[1]/div/span[2]")
    top.click()
    now = datetime.now()
    current_time_in_format = now.strftime("%H:%M:%S")
    print("refreshed fully", current_time_in_format)
    time.sleep(20)



def exception(e):
    browser.refresh()
    time.sleep(2)
    print(e)


def is_element_present(elem):
    try: 
        browser.find_element(by=By.PARTIAL_LINK_TEXT,value=elem)
    except NoSuchElementException as e: return False
    return True


def is_element_present_xpath(elem):
    try: 
        browser.find_element(by=By.XPATH,value = elem)
    except NoSuchElementException as e: return False
    return True


def operate_lift(lifted_count):
    while True:
        lift_url = "http://happytower.mobi/lift"
        browser.get(lift_url) #the link to the lift page on website
        if(is_element_present("Lift to") == True): #the lifting link is present in the form of "lift to XX Floor"
            lift_to = browser.find_element(by=By.PARTIAL_LINK_TEXT,value="Lift to")
            lift_to.click()
            print("lifting")

        #the person has reached the right floor, the link changes to "Get tips XXX"
        elif(is_element_present("Get tips") == True):
            get_tips = browser.find_element(by=By.LINK_TEXT,value="Get tips")
            get_tips.click()
            print(lifted_count," lifted")
            lifted_count += 1

        else:
            return lifted_count


def other_actions(bought_count,collected_count,sold_count):
    while True:
        if(is_element_present("Collect coins!") == True):
            coins = browser.find_element(by=By.LINK_TEXT,value="Collect coins!")
            coins.click()
            print(collected_count," collected")
            collected_count +=1
        
        #sell goods option is present 
        elif(is_element_present("Sell goods") == True):
            sell_goods = browser.find_element(by=By.LINK_TEXT,value = "Sell goods")
            sell_goods.click()
            print(sold_count," sold")
            sold_count +=1

        #buy good option is present
        elif(is_element_present("Buy goods") == True):
            buy()        
            if(is_element_present("Buy for") == False):
                buy()
            else:    
                buy_for = browser.find_element(by=By.PARTIAL_LINK_TEXT,value="Buy for")
                buy_for.click()
                print(bought_count," bought")
                bought_count +=1
        else:
            return [bought_count,collected_count,sold_count]

def special_event():
    browser.get("http://happytower.mobi/fabric")
    if is_element_present("Collect all") == True:
        collect_button = browser.find_element(by=By.PARTIAL_LINK_TEXT,value="Collect all")
        collect_button.click()
        print("pressed collect all special event button")
    elif is_element_present("Start all") == True:
        start_all_button = browser.find_element(by=By.PARTIAL_LINK_TEXT,value="Start all")
        start_all_button.click()
        print("pressed start all special event button")

def signin():
    browser.get("http://happytower.mobi/login")
    nickname = browser.find_element(by=By.XPATH,value ="/html/body/div/div[2]/div/div/div[1]/form/label[1]/input")
    nickname.send_keys(HT_user)
    time.sleep(2)
    password = browser.find_element(by=By.XPATH,value="/html/body/div/div[2]/div/div/div[1]/form/label[2]/input")
    password.send_keys(HT_pass)
    time.sleep(2)
    password.send_keys(Keys.ENTER)
    time.sleep(2)

    print("Logged in")

"""*****************************************"""

"""*************Main program starts*********"""    
main()


import requests
from config import API_KEY
from win10toast import ToastNotifier
import time
import datetime

notifier = ToastNotifier()

while True:
    response = requests.get("https://api.torn.com/torn/?selections=searchforcash&key="+ API_KEY).json()
    search_the_junkyard = response["searchforcash"]["search_the_junkyard"]
    crushing_percentage = search_the_junkyard["percentage"]
    time_now = datetime.datetime.now()

    if crushing_percentage <= 49:
        notifier.show_toast("Search for cash time: Junkyard","Crushing is lower than 49%", duration = 25)
        print(f"Crushing was lower than 49% at {time_now}\n")
    else:
        print(f"checked at {time_now}\n")
    time.sleep(600)
import requests
from win11toast import toast
import time
import datetime

while True:
    time_now = datetime.datetime.now()
    api_response = requests.get(f'https://api.torn.com/torn/?selections=shoplifting&key=D7WpGE3hNr8SJGuL&comment=Tracking').json()
    jewelry_store = api_response["shoplifting"]["jewelry_store"]
    if jewelry_store[1]["disabled"]  == True and jewelry_store[0]["disabled"] == True:
        toast('Cameras disabled and guards on break at jewelry store', 'Click to open page', on_click='https://www.torn.com/loader.php?sid=crimes#/shoplifting')
        print("Cameras disabled and guards on break at jewelry store")
    else:
        print(f"checked at {time_now}\n")
        t =0
    time.sleep(300)
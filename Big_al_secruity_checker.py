import requests
from config import API_KEY
from win10toast import ToastNotifier
import time
import datetime

notifier = ToastNotifier()

while True:
    response = requests.get("https://api.torn.com/torn/?selections=shoplifting&key="+ API_KEY).json()
    shoplifting_big_als = response["shoplifting"]["big_als"]
    cameras_status = shoplifting_big_als[0]["disabled"] #false = active
    guards_status = shoplifting_big_als[1]["disabled"]
    time_now = datetime.datetime.now()

    with open("D:\Downloads\\Big al's secruity record.txt","a") as text_file:
        if cameras_status and guards_status:
            notifier.show_toast("Big als is vulnerable right now!","shoplifting time!", duration = 25)
            text_file.write(f"wale s vulnerable at {time_now}\n")
            print(f"was vulnerabat {time_now}\n")
        elif cameras_status:
            text_file.write(f"no cameras at {time_now}\n")
            print(f"no cameras at {time_now}\n")
            
        elif guards_status:
            text_file.write(f"guards took a break at {time_now}\n")
            print(f"guards took a break at {time_now}\n")
        else:
            text_file.write(f"ran at {time_now}\n")
            print(f"ran at {time_now}\n")
        text_file.close()
        time.sleep(900)


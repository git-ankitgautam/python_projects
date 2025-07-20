import time
import requests 
import json
from datetime import datetime
from config import API_KEY, fac_Ids

cleared = 0
cutoff_hours = 10
now = datetime.now()
current_time = now.timestamp()
activity_cutoff = int(current_time) - (cutoff_hours*60*60) #10 hours

for x in range(len(fac_Ids)):
    write_data = []
    faction_data = requests.get("https://api.torn.com/faction/"+str(fac_Ids[x])+"?selections=&key="+ API_KEY).json()
    faction_name = faction_data["name"]
    print(faction_name)
    with open("Devlins_activity_roundup.txt", "a") as A:
        A.write("In " + faction_name +":\n")
        faction_members_data = faction_data["members"]
        for ids in faction_members_data:
            member_last_action_timestamp = faction_members_data[ids]["last_action"]["timestamp"]
            if member_last_action_timestamp > activity_cutoff:
                cleared +=1
                member_name = faction_members_data[ids]["name"]
                member_last_action_realtive = faction_members_data[ids]["last_action"]["relative"]
                A.write(member_name + "\t\t" + member_last_action_realtive +"\n")
        A.write("number of cumulative members clearing cutoff: " + str(cleared) + "\n\n")
    time.sleep(3)
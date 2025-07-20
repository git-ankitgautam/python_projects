import sys
import time
import requests
import json
from config import API_KEY

my_api = API_KEY
api = API_KEY  #Enter the api of the RW faction leader or AA member
war_id = 17584    #war id to use and fetch war report data from API
faction_id = 39960 #faction id to indetify members of the report generating faction from the API response
report_filename = "BSSEP24" # code for the RW, in the format factioncodeMonthyear

chain_bonus_hits_number_list = [25,50,100,250,500,1000,2500,5000,10000,25000,50000,100000]

"""----------------------------All this is for processing war data each time the script is run-----------------------------"""
member_names = []
member_ids = []
war_Respect = []
war_hits = []
war_start_timestamp = 0
war_end_timestamp = 0

# Fetching war attacks, war score, member names , member ids and war start and end time from the API
def fetch_war_data(war_id, faction_id):
    global war_start_timestamp
    global war_end_timestamp
    war_report_url = "https://api.torn.com/torn/" + str(war_id) + "?selections=rankedwarreport&key=" + api
    war_data_api_reponse_json = requests.get(war_report_url).json()
    war_start_timestamp = str(war_data_api_reponse_json["rankedwarreport"]["war"]["start"])
    war_end_timestamp = str(war_data_api_reponse_json["rankedwarreport"]["war"]["end"] + 1)
    members_war_data = war_data_api_reponse_json["rankedwarreport"]["factions"][str(faction_id)]["members"]
    for member_ids_war_data in members_war_data:
        member_ids.append(int(member_ids_war_data))
        member_names.append(members_war_data[member_ids_war_data]["name"])
        war_hits.append(int(members_war_data[member_ids_war_data]["attacks"]))
        war_Respect.append(members_war_data[member_ids_war_data]["score"])
    with open(report_filename+ ".warData"+ ".txt","w") as war_data_txt_file:
        war_data_txt_file.write(war_start_timestamp + "\n")
        war_data_txt_file.write(war_end_timestamp + "\n")            
        for loop_variable in range(len(member_ids)):
            war_data_txt_file.write(member_names[loop_variable] + "\t\t\t" + str(member_ids[loop_variable]) + "\t\t\t" + str(war_hits[loop_variable]) + "\t\t\t" + str(war_Respect[loop_variable]))
            war_data_txt_file.write("\n")
    war_data_txt_file.close()
    print(member_names)
    print("war data noted")

try:
    fetch_war_data(war_id,faction_id)
    print(war_start_timestamp, war_end_timestamp)
    print("war data loaded successfully")

except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("Exception message:", exc_value)
    print("member names failed", exc_type)
    print("exiting now")
    exit()

"""-----------------------------------FUNCTIONSSS-----------------------------"""
def assists(player_to_check):
    f =0
    with open(report_filename + ".attacks"+ ".txt",'r') as attacks_txt_file: 
        read = attacks_txt_file.read()
    attacks_txt_file.close()
    data  = json.loads(read)
    for key in data:
        attacker_id = data[key]["attacker_id"]
        if attacker_id == player_to_check:
            result = data[key]["result"]
            if str(result) == "Assist":
                f+=1
    return f


def fetch_attacks(start,end):
    print("Fetching attacks....")
    current_end_timestamp = start
    attack_timestamp_steps = []
    with open(report_filename + ".attacks"+ ".txt", 'a') as a:
        while int(end) > int(current_end_timestamp):
            try:
                url = "https://api.torn.com/faction/?selections=attacks&from=" + str(current_end_timestamp) +"&to=" + end + "&key="+ api
                print(url)
                data = requests.get(url).json()
                if len(data["attacks"]) != 0: #checks if the response is empty
                    for key in data["attacks"]:
                        current_end_timestamp = data["attacks"][key]["timestamp_started"] +1
                    print("curently fetched till: " + str(current_end_timestamp))
                    if current_end_timestamp not in attack_timestamp_steps: # chceks if a single attacks is fetched repeatedly
                        first_key = list(data["attacks"].keys())[0]
                        data = {key: value for key, value in data["attacks"].items() if key != first_key}
                        data = json.dumps(data, ensure_ascii=False)
                        a.write(str(data))
                        time.sleep(3)
                        attack_timestamp_steps.append(current_end_timestamp)
                    else:
                        break
                else:
                    break
            except Exception as e:
                print(e)
                print("the above API exception occured, please delete the attacks.txt file, and run this command again!")
                print("exiting the program")
                exit()
    print("attacks noted")

def numpy_sorted_array(unsorted_array):
    import numpy as np
    numpy_array = np.array(unsorted_array)
    sorted_numpy_array = np.argsort(-numpy_array)
    return sorted_numpy_array

def testing_function():
    def chain_hits_counter(player_id):
        count = 0
        with open(report_filename + ".attacks"+ ".txt",'r') as r: 
            read = r.read()
        data  = json.loads(read)
        for key in data:
            attacker_id = data[key]["attacker_id"]
            war_check = data[key]["modifiers"]["war"]
            hit_number = data[key]["chain"]
            if attacker_id == player_id and war_check != 2 and hit_number > 10:
                count+=1
        return count

    chain_hits_list = []
    for x in range(len(member_ids)):
        chain_hit = chain_hits_counter(member_ids[x])
        chain_hits_list.append(chain_hit)
    with open(report_filename+".chain_hits"+ ".txt",'w') as w:
        for loop_variable in range(len(member_names)):
            w.write(str(member_names[loop_variable]) + "\t\t\t" + str(chain_hits_list[loop_variable])+"\n")

    print(chain_hits_list)
    print("chain hits counted successfully")    


def overall_respect_earned(player_to_check):
    hit_respect= respect_earned = 0
    with open(report_filename + ".attacks"+ ".txt",'r') as r:
        read = r.read()
    data  = json.loads(read)
    for key in data:
        attacker_id = data[key]["attacker_id"]
        if attacker_id == player_to_check:
            hit_respect = data[key]["respect"]
            respect_earned += hit_respect
    return respect_earned


def overall_hit_count(player_to_check):
    hit_count= 0
    with open(report_filename + ".attacks"+ ".txt",'r') as r:
        read = r.read()
    data  = json.loads(read)
    for key in data:
        attacker_id = data[key]["attacker_id"]
        if attacker_id == player_to_check:
            if data[key]["result"] != "Lost" and data[key]["result"] != "Timeout":
                hit_count += 1
    return hit_count


def place_data_in_excel():
    from openpyxl import Workbook, load_workbook
    wbk = Workbook()
    main_sheet = wbk.active
    x = y =0
    corrected_index = numpy_sorted_array(war_hits)
    main_sheet["A1"] = "Names"
    main_sheet["b1"] = "War Hits"
    main_sheet["c1"] = "War Score"
    main_sheet["d1"] = "Overall Respect Earned"
    main_sheet["e1"] = "Bonuses"
    main_sheet["g1"] = "Assists"
    main_sheet["f1"] = "Respect lost"
    main_sheet["h1"] = "Overall hit count"
    for x in corrected_index:
        main_sheet[f"A{y+2}"] = member_names[x] +" [" + str(member_ids[x]) +"]"
        main_sheet[f"B{y+2}"] = war_hits[x]
        main_sheet[f"C{y+2}"] = war_Respect[x]
        main_sheet[f"D{y+2}"] = overall_respect_list[x]
        main_sheet[f"E{y+2}"] = bonus_hits_list[x]
        main_sheet[f"F{y+2}"] = respect_lost_list[x]
        main_sheet[f"g{y+2}"] = assist_hits_list[x]
        main_sheet[f"H{y+2}"] = hit_count_list[x]
        y +=1
    wbk.save(report_filename + ".xlsx")
    print("excel saved successfully")


def positive_bonus_hits(player_to_check,respect_gain):
    hit_respect=0
    with open(report_filename + ".attacks"+ ".txt",'r') as r: 
        read = r.read()
    data  = json.loads(read)
    for key in data:
        attacker_id = data[key]["attacker_id"]
        if attacker_id == player_to_check:
            chain_bonus = data[key]["chain"]
            if chain_bonus in chain_bonus_hits_number_list:
                hit_respect = data[key]["respect"]
                respect_gain += hit_respect
    return respect_gain


def respect_loss(player_to_check):
    total_respect_lost = hit_respect = 0
    with open(report_filename + ".attacks"+ ".txt",'r') as r:
        read = r.read()
    data  = json.loads(read)
    for key in data:
        defender_id = data[key]["defender_id"]
        if defender_id == player_to_check:
            war_check = data[key]["modifiers"]["war"]
            if war_check == 2:
                hit_respect = data[key]["respect"]
                total_respect_lost += hit_respect
    return total_respect_lost


def replace_characters_in_file():
    with open(report_filename + ".attacks"+ ".txt",'r') as r:
        read = r.read()
    
    replaced_content = read.replace('}{', ", ")
    
    with open(report_filename + ".attacks"+ ".txt", 'w') as file:
        file.write(replaced_content)
    print("File contents changed to fit the script successfully")


"""----------------------MAIN-----------------------------------------"""
print("Enter 0 for running test function")
choice = int(input())

"""----------------------------- TESTING FUNCTION ----------------------------------"""
if choice == 0:    
    testing_function()
    
"""------------------------- featching attacks ----------------------------"""
if choice != 0:
    fetch_attacks(war_start_timestamp, war_end_timestamp)
    replace_characters_in_file()


    """----------------------------- Assists ----------------------------------"""

    assist_hits_list = []
    for x in range(len(member_ids)):
        assist = assists(member_ids[x])
        assist_hits_list.append(assist)
    with open(report_filename+".assists"+ ".txt",'w') as w:
        for loop_variable in range(len(member_names)):
            w.write(str(member_names[loop_variable]) + "\t\t\t" + str(assist_hits_list[loop_variable])+"\n")

    print(assist_hits_list)
    print("assists counted successfully")

    """----------------------------- Overall respect earned ----------------------------------"""

    overall_respect_list = []
    for x in range(len(member_ids)):
        respect_earned = overall_respect_earned(member_ids[x])
        overall_respect_list.append(respect_earned)
    with open(report_filename+".overall_respect_earned"+ ".txt",'w') as w:
        for loop_variable in range(len(member_names)):
            w.write(str(member_names[loop_variable]) + "\t\t\t" + str(round(overall_respect_list[loop_variable],2))+"\n")

    print(overall_respect_list)
    print("Overall respect earned counted successfully")

    """----------------------------- Respect lost per member ----------------------------------"""

    respect_lost_list = []
    for x in range(len(member_ids)):
        respect_lost = respect_loss(member_ids[x])
        respect_lost_list.append(respect_lost)
    with open(report_filename+".respect_lost"+ ".txt",'w') as w:
        for loop_variable in range(len(member_names)):
            w.write(str(member_names[loop_variable]) + "\t\t\t" + str(round(respect_lost_list[loop_variable],2))+"\n")

    print(respect_lost_list)
    print("Respect lost per member counted successfully")
    """----------------------------- Bonus Hits respect ----------------------------------"""

    bonus_hits_list = []
    for x in range(len(member_ids)):
        bonus = positive_bonus_hits(member_ids[x],respect_gain=0)
        bonus_hits_list.append(bonus)
    with open(report_filename +".positive_bonuses"+ ".txt","w") as w:
        for b in range(len(member_names)):
            w.write(str(member_names[b]) + "\t\t\t" + str(round(bonus_hits_list[b],2))+"\n")

    print(bonus_hits_list)
    print("Bonus hits counted successfully")
    
    """-----------------------------Overall Hit count----------------------------------"""

    hit_count_list = []
    for x in range(len(member_ids)):
        hit_count = overall_hit_count(member_ids[x])
        hit_count_list.append(hit_count)
    with open(report_filename +".overall_hit_count"+ ".txt","w") as w:
        for b in range(len(member_names)):
            w.write(str(member_names[b]) + "\t\t\t" + str(round(hit_count_list[b],2))+"\n")

    print(hit_count_list)
    print("Overall hits counted successfully")
    print("Data processing completed successfully")

    place_data_in_excel()


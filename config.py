from os import environ
from dotenv import load_dotenv
load_dotenv()

try:
    API_KEY = environ["Torn_API_KEY"]
    Tiwar_user = environ["Tiwar_user"]
    Tiwar_pass = environ["Tiwar_pass"]
    HT_user = environ["HT_user"]
    HT_pass = environ["HT_pass"]
    youtube_api_key = environ["yt_api_key"]
    """ for devlins faction ids"""
    fac_Ids = environ["Devlins_faction_ids"]
    fac_Ids= fac_Ids.split(",")
    fac_Ids = [int(num) for num in fac_Ids]
except:
    ...



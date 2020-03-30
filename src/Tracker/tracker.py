import requests
import json

CONFIG_FILE_PATH = "/home/kevin/p/corona-bot/config.json"
COUNTRIES_FILE_PATH = "/home/kevin/p/corona-bot/src/Tracker/contries.json"
TRACK_FILE_PATH = "/home/kevin/p/corona-bot/src/Tracker/track.json"

with open(CONFIG_FILE_PATH) as config_file:
    config = json.load(config_file)

TRACKER_API = config["tracker-api"]

TRACK_ALL = TRACKER_API + "all"
track_all_response = requests.get(TRACK_ALL)
ALL = track_all_response.json()

TRACK_COUNTRIES = TRACKER_API + "countries"
track_countries_response = requests.get(TRACK_COUNTRIES)
COUNTRIES = track_countries_response.json()

TRACK = {
    "all": ALL,
    "top-countries": {
        0: COUNTRIES[0],
        1: COUNTRIES[1],
        2: COUNTRIES[2],
        3: COUNTRIES[3],
        4: COUNTRIES[4]
    },
    "countries": COUNTRIES
}

JSON_COUNTRIES_TEXT = """{

"""
for country_num in range(len(COUNTRIES)):
    JSON_COUNTRIES_TEXT += f"  \"{COUNTRIES[country_num]['country']}\": {country_num},\n"
JSON_COUNTRIES_TEXT += "  \"END\":null\n}"

with open(TRACK_FILE_PATH, "w") as track_file:
    track = json.dump(TRACK, track_file)

countries_file = open(COUNTRIES_FILE_PATH, "w")
countries_file.write(JSON_COUNTRIES_TEXT)
countries_file.close()

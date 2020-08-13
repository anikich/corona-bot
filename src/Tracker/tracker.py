from requests import get as requests_get
from json import load as json_load
from json import dump as jsob_dump
fron os import chdir

chdir("../..")

CONFIG_FILE_PATH = "config.json"

chdir("src/Tracker")

TRACK_FILE_PATH = "track.json"
COUNTRIES_SPELL_PATH = "spells.txt"

spells = open(COUNTRIES_SPELL_PATH, "w")

with open(CONFIG_FILE_PATH) as config_file:
    config = json_load(config_file)

TRACKER_API = config["tracker-api"]

TRACK_ALL = TRACKER_API + "all"
track_all_response = requests_get(TRACK_ALL)
ALL = track_all_response.json()

TRACK_COUNTRIES = TRACKER_API + "countries"
track_countries_response = requests_get(TRACK_COUNTRIES)
COUNTRIES = track_countries_response.json()

countries_spells = ""
for countries_position in range(len(COUNTRIES)):
    countries_spells += f"{COUNTRIES[countries_position]['country']}\n"

spells.write(countries_spells)
spells.close()

countries_json = {}

for country_num in range(len(COUNTRIES)):
    country_name = COUNTRIES[country_num]['country']
    countries_json[country_name] = []
    countries_json[country_name].append(
        {
            "position": country_num,
            "active": COUNTRIES[country_num]["active"],
            "cases": COUNTRIES[country_num]["cases"],
            "casesPerOneMillion": COUNTRIES[country_num]["casesPerOneMillion"],
            "critical": COUNTRIES[country_num]["critical"],
            "deaths": COUNTRIES[country_num]["deaths"],
            "deathsPerOneMillion": COUNTRIES[country_num]["deathsPerOneMillion"],
            "recovered": COUNTRIES[country_num]["recovered"],
            "todayCases": COUNTRIES[country_num]["todayCases"],
            "todayDeaths": COUNTRIES[country_num]["todayDeaths"]
        }
    )

COUNTRIES_BY_NAME = countries_json

TRACK = {
    "all": ALL,
    "top-countries": {
        0: COUNTRIES[0],
        1: COUNTRIES[1],
        2: COUNTRIES[2],
        3: COUNTRIES[3],
        4: COUNTRIES[4]
    },
    "countries": COUNTRIES_BY_NAME
}

with open(TRACK_FILE_PATH, "w") as track_file:
    track = json_dump(TRACK, track_file, sort_keys=True, indent=2)

import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)

from telegram import (ParseMode, ReplyKeyboardMarkup)
from difflib import get_close_matches
import matplotlib.pyplot as plt

CONFIG_PATH = "config.json"
PLOT_PATH = "src/bot/f.png"
TRACK_PATH = "src/Tracker/track.json"

with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)

TOKEN = config["telegram-token"]
ADMIN_ID = config["admin_chat_id"]

SPELL_PATH = "src/Tracker/spells.txt"
spell_file = open(SPELL_PATH, "r")

spells_list = []
for spells in spell_file.readlines():
    spells_list.append(spells.replace("\n", ""))
def spell_check(spell):
    check_spell = get_close_matches(spell, spells_list)
    if spell in spells_list:
        return True

    elif len(check_spell) > 0:
        return f"Did you mean: {check_spell[0]} ?"

    elif spell not in spells_list:
        return "Wrong country name!"

START_TEXT = "Send country name: "

updater = Updater(TOKEN)
dp = updater.dispatcher

class Extractor:
    country_cases = None
    country_deaths = None
    country_recovered = None
    country_today_cases = None
    country_today_deaths = None
    country_cases_per_mill = None
    country_deaths_per_mill = None
    country_position = None
    country_first_case = None

    def __init__(self, path):
        self.path = path

        with open(self.path) as track_file:
            self.track = json.load(track_file)

    def by_country(self, country_name):
        from_country = self.track["countries"][country_name][0]

        Extractor.country_deaths = from_country["deaths"]
        Extractor.country_cases = from_country["cases"]
        Extractor.country_recovered = from_country["recovered"]

        Extractor.country_today_cases = from_country["todayCases"]
        Extractor.country_today_deaths = from_country["todayDeaths"]

        Extractor.country_cases_per_mill = from_country["casesPerOneMillion"]
        Extractor.country_deaths_per_mill = from_country["deathsPerOneMillion"]

        Extractor.country_position = from_country["position"]

        param = ["Cases", "Recovered", "Deaths"]
        unit = [
            Extractor.country_cases,
            Extractor.country_recovered,
            Extractor.country_deaths
        ]

        plot = plt.bar(param, unit)
        plot[0].set_color('#9E5BD4')

        ax = plt.axes()

        if Extractor.country_recovered < Extractor.country_cases/2:
            plot[1].set_color('#E0E05E')
        elif Extractor.country_recovered < (Extractor.country_cases/2)/2:
            plot[1].set_color('#B74B4B')
        elif Extractor.country_recovered > Extractor.country_cases / 2:
            plot[1].set_color('#62DC62')
        else:
            plot[2].set_color('#62DC62')

        if Extractor.country_deaths <= (Extractor.country_recovered/2)/2:
            plot[2].set_color('#62DC62')
        elif (Extractor.country_deaths >= Extractor.country_recovered/2) and\
                (Extractor.country_deaths <= Extractor.country_recovered):
            plot[2].set_color('#E0E05E')
        elif Extractor.country_deaths > Extractor.country_recovered:
            plot[2].set_color('#B74B4B')
        else:
            plot[2].set_color('#62DC62')

        for value in plot:
            height = value.get_height()
            plt.text(value.get_x() + value.get_width() / 2., 1.002 * height, '%d' % int(height), ha='center',
                     va='bottom')

        plt.title(f"COVID-19 in {country_name}\n")

        plt.box(False)

        ax.get_yaxis().set_ticks([])
        plt.savefig(PLOT_PATH)
        plt.close()

    def by_position(self, country_position):
        print(self.track["top-countries"][country_position]["deaths"])


ex = Extractor(TRACK_PATH)


def start(bot, update):

    chat_id = update.message.chat.id
    keyboard = ReplyKeyboardMarkup(
        [["Report a bug"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    start.message = bot.sendMessage(
        chat_id=chat_id,
        text=START_TEXT,
        reply_markup=keyboard
    )


def report_bug(bot, update):
    update.message.reply_text("Send your Message: ")

def send_report(bot, update):
    chat_id = update.message.chat.id
    bug = update.message.text
    bot.sendMessage(chat_id=ADMIN_ID,
                    text=bug)
    bot.sendMessage(chat_id=chat_id,
                    text="Successfully sent!")

def show_by_country(bot, update):
    chat_id = update.message.chat.id
    country = update.message.text
    spell_check_result = spell_check(country)
    if type(spell_check_result) == bool:
        ex.by_country(country)
        bot.sendPhoto(parse_mode=ParseMode.MARKDOWN,
                      chat_id=chat_id,
                      photo=open(PLOT_PATH, "rb"),
                      caption=f"""
***ALL:***
  cases: `{Extractor.country_cases}`
  deaths: `{Extractor.country_deaths}`
  recovered: `{Extractor.country_recovered}`
---------------------
***TODAY:***
  cases: `{Extractor.country_today_cases}`
  deaths: `{Extractor.country_today_deaths}`
---------------------
***Per Million:***
  cases: `{Extractor.country_cases_per_mill}`
  deaths: `{Extractor.country_deaths_per_mill}`
----------------------
***Position:*** `{Extractor.country_position}`
        """)

    else:
        update.message.reply_text(spell_check_result)


dp.add_handler(
    CommandHandler("start", start)
)

dp.add_handler(
    MessageHandler(Filters.regex(r"^(Report a bug)$"), report_bug)
)

dp.add_handler(
    MessageHandler(Filters.regex(r"^(#[Bb][Uu][Gg][:=].*)$"), send_report)
)

dp.add_handler(
    MessageHandler(Filters.text, show_by_country)
)

updater.start_polling()

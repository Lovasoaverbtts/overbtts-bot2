import os
import requests
import telegram
import schedule
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

bot = telegram.Bot(token=TOKEN)

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

BASE_URL = "https://v3.football.api-sports.io"


def get_today_matches():
    today = time.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?date={today}"

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    return data["response"]


def analyze_match(match):
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]

    # valeurs temporaires (on remplacera par vraies stats en V3)
    league_avg_goals = 2.8
    odds = 1.85

    home_form = 6
    away_form = 6

    home_home_goals = 4
    away_away_goals = 4

    h2h_over = 3
    h2h_btts = 3

    if league_avg_goals < 2.7:
        return None

    if home_form < 5 or away_form < 5:
        return None

    if home_home_goals < 4 or away_away_goals < 4:
        return None

    if h2h_over >= 3:
        pick = "Over 2.5"
    elif h2h_btts >= 3:
        pick = "BTTS"
    else:
        return None

    if odds < 1.60 or odds > 2.20:
        return None

    return f"""
🔥 OVERBTTS PICK

⚽ {home} vs {away}
🎯 Pick : {pick}
💰 Cote : {odds}
"""


def send_picks():
    matches = get_today_matches()
    picks = []

    for match in matches:
        result = analyze_match(match)
        if result:
            picks.append(result)

        if len(picks) >= 5:
            break

    if len(picks) == 0:
        msg = "❌ Aucun match valide aujourd'hui"
    else:
        msg = "🔥 OVERBTTS DU JOUR 🔥\n\n" + "\n".join(picks)

    bot.send_message(chat_id=CHAT_ID, text=msg)

send_picks()
schedule.every().day.at("08:00").do(send_picks)

print("OverBtts Bot actif...")

while True:
    schedule.run_pending()
    time.sleep(60)

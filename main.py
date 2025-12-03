import requests
import time
import os
from telegram import Bot

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

API_URL = "https://api.sofascore.com/api/v1/sport/handball/events/live"

# REGULI DE ALERTĂ – poți adăuga oricâte
rules = [
    {
        "minut": 20,
        "min_total_goluri": 22,
        "mesaj": "⚡ ALERTĂ: La minutul 20 sunt peste 22 goluri!"
    },
    {
        "minut": 10,
        "echipa_goluri_max": 3,
        "mesaj": "⚡ ALERTĂ: La minutul 10 o echipă are doar 3 goluri!"
    }
]

trimise = set()  # ca să nu trimită aceeași alertă de mai multe ori

def trimite_alerta(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except:
        pass

def verifica_meciuri():
    try:
        r = requests.get(API_URL)
        data = r.json()

        meciuri = data.get("events", [])

        for meci in meciuri:
            minute = meci["time"]["currentPeriodStartTimestamp"]
            status = meci["status"]["type"]

            # skip meciuri în pauză sau oprite
            if status != "inprogress":
                continue

            # minute jucate
            secunde = meci["time"].get("currentPeriodStartTimestamp", 0)
            minut_curent = meci["time"].get("currentPeriodScore", {}).get("period", 0)

            scor_home = meci["homeTeam"]["score"]["current"]
            scor_away = meci["awayTeam"]["score"]["current"]
            total = scor_home + scor_away

            for regula in rules:
                key = f"{meci['id']}-{regula}"

                # regulă pentru total goluri
                if "min_total_goluri" in regula:
                    if minut_curent >= regula["minut"] and total >= regula["min_total_goluri"]:
                        if key not in trimise:
                            trimite_alerta(regula["mesaj"])
                            trimise.add(key)

                # regulă pentru goluri echipă
                if "echipa_goluri_max" in regula:
                    if minut_curent >= regula["minut"]:
                        if scor_home <= regula["echipa_goluri_max"] or scor_away <= regula["echipa_goluri_max"]:
                            if key not in trimise:
                                trimite_alerta(regula["mesaj"])
                                trimise.add(key)

    except Exception as e:
        print("Eroare:", e)

def main():
    trimite_alerta("🤖 Bot de handbal pornit și funcțional!")
    while True:
        verifica_meciuri()
        time.sleep(20)  # verifică la fiecare 20 secunde

if __name__ == "__main__":
    main()

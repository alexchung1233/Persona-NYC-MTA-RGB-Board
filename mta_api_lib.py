import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timezone

load_dotenv()

MTA_API_URL = os.getenv("MTA_API_URL")
ST_LOWERY_40TH = "715"

def get_next_trains(route="7",stop_id=ST_LOWERY_40TH, num=3):
    url = f"{MTA_API_URL}/by-route/{route}"
    response = requests.get(url)
    data = response.json()
    now = datetime.now(timezone.utc)

    for stop in data["data"]:
        if stop["id"] == stop_id:
            north = sorted(stop["N"], key=lambda x: x["time"])[:num]
            south = sorted(stop["S"], key=lambda x: x["time"])[:num]

            def to_minutes(t):
                dt = datetime.fromisoformat(t)
                return int((dt - now).total_seconds() / 60)

            return {
                "N": [{"route": t["route"], "minutes": to_minutes(t["time"])} for t in north],
                "S": [{"route": t["route"], "minutes": to_minutes(t["time"])} for t in south],
            }




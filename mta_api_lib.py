import math
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

    def to_minutes(t):
        dt = datetime.fromisoformat(t)
        # Round up rather than truncate, so a train 10s out reads "1 min"
        # instead of "0 min".
        return math.ceil((dt - now).total_seconds() / 60)

    for stop in data["data"]:
        if stop["id"] == stop_id:
            # GTFS-realtime can keep a stop_time_update around briefly after
            # its predicted time (train still dwelling, or feed hasn't
            # refreshed yet), which showed up here as bogus "-1 min"/"0 min"
            # entries. Drop anything that isn't actually still upcoming.
            upcoming_north = [t for t in stop["N"] if to_minutes(t["time"]) >= 1]
            upcoming_south = [t for t in stop["S"] if to_minutes(t["time"]) >= 1]

            north = sorted(upcoming_north, key=lambda x: x["time"])[:num]
            south = sorted(upcoming_south, key=lambda x: x["time"])[:num]

            return {
                "N": [{"route": t["route"], "minutes": to_minutes(t["time"])} for t in north],
                "S": [{"route": t["route"], "minutes": to_minutes(t["time"])} for t in south],
            }




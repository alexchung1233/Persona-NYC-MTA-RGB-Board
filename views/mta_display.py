from rgbmatrix import graphics
from PIL import Image

import time
from datetime import datetime

import mta_api_lib as api
import route_constants

from .clock_display import ClockDisplay

FONT_PATH = "fonts/helvetica-9.bdf"
LOGO_SIZE = 9
PAIR_SLEEP = 3  # seconds each pair of trains is shown
CLOCK_DURATION = 3  # seconds the clock shows after each full pair cycle
BOTTOM_CLOCK_Y = 29  # baseline for the small clock at the bottom of each frame
PAIRS = [("N", 0), ("S", 0), ("N", 1), ("S", 1)]


class MtaDisplay:
    def __init__(self, matrix, route="7"):
        self.matrix = matrix
        self.route_config = route_constants.ROUTES[route]

        self.font = graphics.Font()
        self.font.LoadFont(FONT_PATH)

        self.logo = Image.open(self.route_config["logo"]).convert("RGB")
        self.logo = self.logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)

        self.clock = ClockDisplay(matrix)

    def draw_direction(self, train_data, direction, pair):
        self.matrix.Clear()
        route_color = graphics.Color(*self.route_config["color"])
        white = graphics.Color(255, 255, 255)

        destination = self.route_config["uptown"] if direction == "N" else self.route_config["downtown"]
        trains = train_data[direction]

        y1, y2 = 10, 22
        i = pair * 2
        labels = (i + 1, i + 2)

        self._draw_row(y1, labels[0], trains[i]["minutes"], destination, route_color, white)
        self._draw_row(y2, labels[1], trains[i + 1]["minutes"], destination, route_color, white)
        self._draw_bottom_clock(white)

    def _draw_row(self, y, label, minutes, destination, route_color, white):
        # Order: index, route logo, destination, time -- e.g. "1 (7) Hudson Yards  3 min"
        x = graphics.DrawText(self.matrix, self.font, 0, y, white, f"{label} ")

        self.matrix.SetImage(self.logo, x, y - LOGO_SIZE)
        x += LOGO_SIZE + 2

        x += graphics.DrawText(self.matrix, self.font, x, y, route_color, f"{destination} ")
        graphics.DrawText(self.matrix, self.font, x, y, white, f" {minutes} min")

    def _draw_bottom_clock(self, white):
        time_text = datetime.now().strftime("%-I:%M %p")
        width = sum(self.font.CharacterWidth(ord(char)) for char in time_text)
        x = (self.matrix.width - width) // 2
        graphics.DrawText(self.matrix, self.font, x, BOTTOM_CLOCK_Y, white, time_text)

    def run(self, duration=None):
        """Cycle through the N/S train pairs, refetching after each full cycle,
        showing the clock for a few seconds between cycles.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed (mid-cycle if need be).
        """
        deadline = time.monotonic() + duration if duration is not None else None

        while deadline is None or time.monotonic() < deadline:
            train_data = api.get_next_trains(num=4)

            # Only show pairs the fetched data actually has two trains for;
            # off-peak/late-night service can return fewer than 4 per direction.
            pairs = [(d, p) for d, p in PAIRS if len(train_data[d]) >= p * 2 + 2]

            if not pairs:
                time.sleep(PAIR_SLEEP)
                continue

            for direction, pair in pairs:
                if deadline is not None and time.monotonic() >= deadline:
                    return
                self.draw_direction(train_data, direction, pair)
                time.sleep(PAIR_SLEEP)

            if deadline is not None and time.monotonic() >= deadline:
                return
            self.clock.run(duration=CLOCK_DURATION)

from rgbmatrix import graphics
from PIL import Image

import time
import mta_api_lib as api
import route_constants

FONT_PATH = "fonts/helvetica-9.bdf"
LOGO_SIZE = 9
PAIR_SLEEP = 5  # seconds each pair of trains is shown
PAIRS = [("N", 0), ("S", 0), ("N", 1), ("S", 1)]


class MtaDisplay:
    def __init__(self, matrix, route="7"):
        self.matrix = matrix
        self.route_config = route_constants.ROUTES[route]

        self.font = graphics.Font()
        self.font.LoadFont(FONT_PATH)

        self.logo = Image.open(self.route_config["logo"]).convert("RGB")
        self.logo = self.logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
        self.text_x = LOGO_SIZE + 2

    def draw_direction(self, train_data, direction, pair):
        self.matrix.Clear()
        route_color = graphics.Color(*self.route_config["color"])
        white = graphics.Color(255, 255, 255)

        destination = self.route_config["uptown"] if direction == "N" else self.route_config["downtown"]
        trains = train_data[direction]

        y1, y2 = 10, 22
        i = pair * 2
        labels = (i + 1, i + 2)

        self.matrix.SetImage(self.logo, 0, y1 - LOGO_SIZE)
        self.matrix.SetImage(self.logo, 0, y2 - LOGO_SIZE)

        idx1_len = graphics.DrawText(self.matrix, self.font, self.text_x, y1, white, f"{labels[0]} ")
        name_len = graphics.DrawText(self.matrix, self.font, self.text_x + idx1_len, y1, route_color, destination)
        graphics.DrawText(self.matrix, self.font, self.text_x + idx1_len + name_len, y1, white, f"  {trains[i]['minutes']} min")

        idx2_len = graphics.DrawText(self.matrix, self.font, self.text_x, y2, white, f"{labels[1]} ")
        name_len = graphics.DrawText(self.matrix, self.font, self.text_x + idx2_len, y2, route_color, destination)
        graphics.DrawText(self.matrix, self.font, self.text_x + idx2_len + name_len, y2, white, f"  {trains[i + 1]['minutes']} min")

    def run(self, duration=None):
        """Cycle through the N/S train pairs, refetching after each full cycle.

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

from rgbmatrix import graphics
from PIL import Image

import time
from datetime import datetime

LOGO_PATH = "assets/knicks-logo.png"
FONT_PATH = "fonts/nba-knicks-16.bdf"
LOGO_GAP = 4  # pixels between the logo and the time
REFRESH = 1  # seconds between time redraws

KNICKS_ORANGE = graphics.Color(245, 132, 38)

# The Knicks font has no colon glyph, so the time is space-separated
# instead of "H:MM" (e.g. "3 07 PM").
TIME_FORMAT = "%-I %M %p"


class ClockDisplay:
    def __init__(self, matrix):
        self.matrix = matrix

        self.font = graphics.Font()
        self.font.LoadFont(FONT_PATH)

        # Flatten the logo's transparency onto a black background so it renders
        # cleanly on the panel instead of showing stray colors from transparent pixels.
        logo_rgba = Image.open(LOGO_PATH).convert("RGBA")
        logo_bg = Image.new("RGB", logo_rgba.size, (0, 0, 0))
        logo_bg.paste(logo_rgba, mask=logo_rgba.split()[3])

        self.logo_height = matrix.height
        self.logo_width = int(logo_rgba.width * (self.logo_height / logo_rgba.height))
        self.logo = logo_bg.resize((self.logo_width, self.logo_height), Image.LANCZOS)
        self.logo_y = (matrix.height - self.logo_height) // 2

        self.text_y = (matrix.height - self.font.height) // 2 + self.font.baseline

    def _text_width(self, text):
        return sum(self.font.CharacterWidth(ord(char)) for char in text)

    def run(self, duration=None):
        """Show the Knicks logo and current time, centered on the panel.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed.
        """
        deadline = time.monotonic() + duration if duration is not None else None

        while deadline is None or time.monotonic() < deadline:
            time_text = datetime.now().strftime(TIME_FORMAT)
            group_width = self.logo_width + LOGO_GAP + self._text_width(time_text)
            x = (self.matrix.width - group_width) // 2

            self.matrix.Clear()
            self.matrix.SetImage(self.logo, x, self.logo_y)
            graphics.DrawText(self.matrix, self.font, x + self.logo_width + LOGO_GAP, self.text_y, KNICKS_ORANGE, time_text)

            time.sleep(REFRESH)

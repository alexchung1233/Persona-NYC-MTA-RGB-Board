from rgbmatrix import graphics
from PIL import Image

import time
from datetime import datetime

LOGO_PATH = "assets/knicks-logo.png"
FONT_PATH = "fonts/nba-knicks-16.bdf"
LOGO_GAP = 4  # pixels between the logo and the time
REFRESH = 1  # seconds between time redraws

KNICKS_ORANGE = graphics.Color(245, 132, 38)

# The Knicks font has no colon glyph, so it's hand-drawn as two dots.
COLON_DOT_SIZE = 2
COLON_PADDING = 1  # pixels on each side of the dots


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

    def _draw_colon(self, x, color):
        # Two square dots spanning the digits' cap-height, in place of a colon glyph.
        cap_height = self.font.baseline
        top = self.text_y - round(cap_height * 0.72)
        bottom = self.text_y - round(cap_height * 0.28)

        for dy in range(COLON_DOT_SIZE):
            for dx in range(COLON_DOT_SIZE):
                self.matrix.SetPixel(x + COLON_PADDING + dx, top + dy, color.red, color.green, color.blue)
                self.matrix.SetPixel(x + COLON_PADDING + dx, bottom + dy, color.red, color.green, color.blue)

        return COLON_PADDING + COLON_DOT_SIZE + COLON_PADDING

    def run(self, duration=None):
        """Show the Knicks logo and current time, centered on the panel.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed.
        """
        deadline = time.monotonic() + duration if duration is not None else None

        while deadline is None or time.monotonic() < deadline:
            now = datetime.now()
            hour = now.strftime("%-I")
            minute = now.strftime("%M")
            am_pm = f" {now.strftime('%p')}"

            colon_width = COLON_PADDING + COLON_DOT_SIZE + COLON_PADDING
            time_width = self._text_width(hour) + colon_width + self._text_width(minute) + self._text_width(am_pm)
            x = (self.matrix.width - (self.logo_width + LOGO_GAP + time_width)) // 2

            self.matrix.Clear()
            self.matrix.SetImage(self.logo, x, self.logo_y)
            x += self.logo_width + LOGO_GAP

            x += graphics.DrawText(self.matrix, self.font, x, self.text_y, KNICKS_ORANGE, hour)
            x += self._draw_colon(x, KNICKS_ORANGE)
            x += graphics.DrawText(self.matrix, self.font, x, self.text_y, KNICKS_ORANGE, minute)
            graphics.DrawText(self.matrix, self.font, x, self.text_y, KNICKS_ORANGE, am_pm)

            time.sleep(REFRESH)

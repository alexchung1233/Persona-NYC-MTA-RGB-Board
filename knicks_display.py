from rgbmatrix import graphics
from PIL import Image

import time

LOGO_PATH = "assets/knicks-logo.png"
FONT_PATH = "fonts/nba-knicks-16.bdf"
SCROLL_SPEED = 0.03  # seconds between frames; lower is faster
LOGO_GAP = 4  # pixels between the logo and the text

KNICKS_BLUE = graphics.Color(0, 107, 182)
KNICKS_ORANGE = graphics.Color(245, 132, 38)

WORDS = [
    ("KNICKS ", KNICKS_BLUE),
    ("IN ", KNICKS_ORANGE),
    ("FIVE", KNICKS_BLUE),
]


class KnicksDisplay:
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

        self.text_width = sum(self.font.CharacterWidth(ord(char)) for word, _ in WORDS for char in word)
        self.text_y = (matrix.height - self.font.height) // 2 + self.font.baseline

        self.group_width = self.text_width + LOGO_GAP + self.logo_width

    def run(self, duration=None):
        """Scroll the logo and text together, left to right, on a loop.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed (mid-scroll if need be).
        """
        deadline = time.monotonic() + duration if duration is not None else None

        canvas = self.matrix.CreateFrameCanvas()
        x_group = -self.group_width

        while deadline is None or time.monotonic() < deadline:
            x_group += 1
            if x_group > canvas.width:
                x_group = -self.group_width

            canvas.Clear()
            canvas.SetImage(self.logo, x_group, self.logo_y)

            x = x_group + self.logo_width + LOGO_GAP
            for word, color in WORDS:
                x += graphics.DrawText(canvas, self.font, x, self.text_y, color, word)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(SCROLL_SPEED)

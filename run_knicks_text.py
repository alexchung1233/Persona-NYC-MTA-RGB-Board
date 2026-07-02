from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

import os
import time
from dotenv import load_dotenv

load_dotenv()

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

options = RGBMatrixOptions()
options.rows = int(os.getenv("ROWS"))
options.cols = int(os.getenv("COLS"))
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont(FONT_PATH)

# Flatten the logo's transparency onto a black background so it renders
# cleanly on the panel instead of showing stray colors from transparent pixels.
logo_rgba = Image.open(LOGO_PATH).convert("RGBA")
logo_bg = Image.new("RGB", logo_rgba.size, (0, 0, 0))
logo_bg.paste(logo_rgba, mask=logo_rgba.split()[3])

logo_height = matrix.height
logo_width = int(logo_rgba.width * (logo_height / logo_rgba.height))
logo = logo_bg.resize((logo_width, logo_height), Image.LANCZOS)
logo_y = (matrix.height - logo_height) // 2

text_width = sum(font.CharacterWidth(ord(char)) for word, _ in WORDS for char in word)
text_y = (matrix.height - font.height) // 2 + font.baseline

group_width = text_width + LOGO_GAP + logo_width

canvas = matrix.CreateFrameCanvas()
x_group = -group_width

try:
    while True:
        x_group += 1
        if x_group > canvas.width:
            x_group = -group_width

        canvas.Clear()

        canvas.SetImage(logo, x_group, logo_y)

        x = x_group + logo_width + LOGO_GAP
        for word, color in WORDS:
            x += graphics.DrawText(canvas, font, x, text_y, color, word)
        canvas = matrix.SwapOnVSync(canvas)

        time.sleep(SCROLL_SPEED)

except KeyboardInterrupt:
    matrix.Clear()

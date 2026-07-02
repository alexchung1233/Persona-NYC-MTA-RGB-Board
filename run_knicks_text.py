from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

import os
import time
from dotenv import load_dotenv

load_dotenv()

LOGO_PATH = "assets/knicks-logo.png"
SCROLL_SPEED = 0.03  # seconds between frames; lower is faster

options = RGBMatrixOptions()
options.rows = int(os.getenv("ROWS"))
options.cols = int(os.getenv("COLS"))
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

# Flatten the logo's transparency onto a black background so it renders
# cleanly on the panel instead of showing stray colors from transparent pixels.
logo_rgba = Image.open(LOGO_PATH).convert("RGBA")
logo_bg = Image.new("RGB", logo_rgba.size, (0, 0, 0))
logo_bg.paste(logo_rgba, mask=logo_rgba.split()[3])

logo_height = matrix.height
logo_width = int(logo_rgba.width * (logo_height / logo_rgba.height))
logo = logo_bg.resize((logo_width, logo_height), Image.LANCZOS)

logo_y = (matrix.height - logo_height) // 2

canvas = matrix.CreateFrameCanvas()
x_pos = -logo_width

try:
    while True:
        x_pos += 1
        if x_pos > canvas.width:
            x_pos = -logo_width

        canvas.Clear()
        canvas.SetImage(logo, x_pos, logo_y)
        canvas = matrix.SwapOnVSync(canvas)

        time.sleep(SCROLL_SPEED)

except KeyboardInterrupt:
    matrix.Clear()

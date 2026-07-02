from rgbmatrix import RGBMatrix, RGBMatrixOptions

import os
from dotenv import load_dotenv

load_dotenv()


def create_matrix():
    options = RGBMatrixOptions()
    options.rows = int(os.getenv("ROWS"))
    options.cols = int(os.getenv("COLS"))
    options.hardware_mapping = 'adafruit-hat'

    return RGBMatrix(options=options)

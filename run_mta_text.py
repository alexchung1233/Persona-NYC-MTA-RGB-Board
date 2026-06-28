from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import mta_api_lib as api
import route_constants as route_constants

import time
import os
from dotenv import load_dotenv

load_dotenv()

FONT_PATH = "fonts/helvetica-9.bdf"
ROUTES = route_constants.ROUTES

options = RGBMatrixOptions()
options.rows = int(os.getenv("ROWS"))
options.cols = int(os.getenv("COLS"))
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont(FONT_PATH)

route = "7"
route_config = ROUTES[route]

LOGO_SIZE = 9
logo = Image.open(route_config["logo"]).convert("RGB")
logo = logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
TEXT_X = LOGO_SIZE + 2

matrix.Clear()

def draw_direction(train_data, direction):
    matrix.Clear()
    route_color = graphics.Color(*route_config["color"])
    white = graphics.Color(255, 255, 255)

    destination = route_config["uptown"] if direction == "N" else route_config["downtown"]
    trains = train_data[direction]

    y1, y2 = 10, 22

    matrix.SetImage(logo, 0, y1 - LOGO_SIZE)
    matrix.SetImage(logo, 0, y2 - LOGO_SIZE)

    name_len = graphics.DrawText(matrix, font, TEXT_X, y1, route_color, destination)
    graphics.DrawText(matrix, font, TEXT_X + name_len, y1, white, f"  {trains[0]['minutes']} min")

    name_len = graphics.DrawText(matrix, font, TEXT_X, y2, route_color, destination)
    graphics.DrawText(matrix, font, TEXT_X + name_len, y2, white, f"  {trains[1]['minutes']} min")

try:
    while True:
        train_data = api.get_next_trains()

        draw_direction(train_data, "N")
        time.sleep(5)

        draw_direction(train_data, "S")
        time.sleep(5)

except KeyboardInterrupt:
    matrix.Clear()

from rgbmatrix import graphics
from PIL import Image

import time

import weather_api_lib as api

BIG_FONT_PATH = "fonts/sharetech-mono-20.bdf"
SMALL_FONT_PATH = "fonts/sharetech-mono-9.bdf"
ICON_DIR = "assets/weather"
CONDITIONS = ("sunny", "cloudy", "rainy", "snow")
ICON_FILES = {"sunny": "sunny.png", "cloudy": "cloud.png", "rainy": "rainy.png", "snow": "snow.png"}

ICON_GAP = 5  # pixels between the icon and the current temp
COLUMN_GAP = 6  # pixels between the current temp and the high/low column

# Baselines: the big digits span rows 9-22; the 7px-tall high/low lines span
# rows 8-14 and 17-23, bracketing them with a 2px gap between the two.
BIG_BASELINE = 23
HIGH_BASELINE = 15
LOW_BASELINE = 24

CURRENT_COLOR = graphics.Color(0, 229, 255)  # neon cyan
HIGH_COLOR = graphics.Color(255, 110, 64)  # warm orange
LOW_COLOR = graphics.Color(110, 160, 255)  # ice blue


class WeatherDisplay:
    def __init__(self, matrix):
        self.matrix = matrix

        self.big_font = graphics.Font()
        self.big_font.LoadFont(BIG_FONT_PATH)
        self.small_font = graphics.Font()
        self.small_font.LoadFont(SMALL_FONT_PATH)

        self.icons = {
            name: Image.open(f"{ICON_DIR}/{ICON_FILES[name]}").convert("RGB")
            for name in CONDITIONS
        }

    @staticmethod
    def _text_width(font, text):
        return sum(font.CharacterWidth(ord(char)) for char in text)

    def draw(self, weather):
        icon = self.icons[weather["condition"]]
        current = f"{weather['current']}°F"
        high = f"H {weather['high']}°"
        low = f"L {weather['low']}°"

        current_width = self._text_width(self.big_font, current)
        column_width = max(self._text_width(self.small_font, high), self._text_width(self.small_font, low))
        total_width = icon.width + ICON_GAP + current_width + COLUMN_GAP + column_width
        x = max(0, (self.matrix.width - total_width) // 2)

        self.matrix.Clear()
        self.matrix.SetImage(icon, x, (self.matrix.height - icon.height) // 2)
        x += icon.width + ICON_GAP

        x += graphics.DrawText(self.matrix, self.big_font, x, BIG_BASELINE, CURRENT_COLOR, current)
        x += COLUMN_GAP

        graphics.DrawText(self.matrix, self.small_font, x, HIGH_BASELINE, HIGH_COLOR, high)
        graphics.DrawText(self.matrix, self.small_font, x, LOW_BASELINE, LOW_COLOR, low)

    def run(self, duration=None):
        """Show the current NYC weather icon and temps.

        Skips immediately if no weather data is available. Runs forever if
        duration is None, otherwise stops once duration seconds have elapsed.
        """
        weather = api.get_weather()
        if weather is None:
            return

        self.draw(weather)
        if duration is None:
            while True:
                time.sleep(60)
                weather = api.get_weather() or weather
                self.draw(weather)
        time.sleep(duration)

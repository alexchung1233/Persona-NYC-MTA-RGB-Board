from rgbmatrix import graphics
from PIL import Image

import time

import weather_api_lib as api

# Hand-drawn X11 pixel fonts: crisper on the LEDs than scaled TrueType fonts.
BIG_FONT_PATH = "fonts/10x20.bdf"
SMALL_FONT_PATH = "fonts/6x10.bdf"
ICON_DIR = "assets/weather"
CONDITIONS = ("sunny", "cloudy", "rainy", "snow")
ICON_FILES = {"sunny": "sunny.png", "cloudy": "cloud.png", "rainy": "rainy.png", "snow": "snow.png"}

ICON_GAP = 5  # pixels between the icon and the current temp
COLUMN_GAP = 6  # pixels between the current temp and the high/low column

# Baselines: the 13px-tall big digits span rows 10-22; the 7px-tall high/low
# lines span rows 8-14 and 17-23, bracketing them with a 2px gap between.
BIG_BASELINE = 23
HIGH_BASELINE = 15
LOW_BASELINE = 24

# Current temp is color-coded: cold at or below COLD_MAX, hot above HOT_MIN,
# comfortable in between.
COLD_MAX = 50
HOT_MIN = 75
COLD_COLOR = graphics.Color(0, 229, 255)  # icy cyan
GOOD_COLOR = graphics.Color(80, 255, 120)  # mint green
HOT_COLOR = graphics.Color(255, 50, 30)  # hot red
HIGH_COLOR = graphics.Color(255, 110, 64)  # warm orange
LOW_COLOR = graphics.Color(110, 160, 255)  # ice blue


def temp_color(temp):
    """Color for a current temp: cold, comfortable, or hot."""
    if temp <= COLD_MAX:
        return COLD_COLOR
    if temp <= HOT_MIN:
        return GOOD_COLOR
    return HOT_COLOR


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

        x += graphics.DrawText(self.matrix, self.big_font, x, BIG_BASELINE, temp_color(weather["current"]), current)
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

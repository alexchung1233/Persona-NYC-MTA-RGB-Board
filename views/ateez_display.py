from PIL import Image

import time

EMBLEM_PATH = "assets/ateez-logo-2.png"
WORDMARK_PATH = "assets/Ateez-Logo-2018.png"
SCROLL_SPEED = 0.03  # seconds between frames; lower is faster
LOGO_GAP = 6  # pixels between the emblem and the wordmark

# Black artwork would be invisible against the panel's unlit (black) background,
# so the "black & turquoise" scheme is rendered as turquoise + white instead.
EMBLEM_COLOR = (64, 224, 208)
WORDMARK_COLOR = (255, 255, 255)


def _load_logo(path, panel_height, color):
    """Trim transparent padding, scale to panel height, and flatten onto black."""
    logo = Image.open(path).convert("RGBA")
    logo = logo.crop(logo.getbbox())

    width = int(logo.width * (panel_height / logo.height))
    logo = logo.resize((width, panel_height), Image.LANCZOS)
    alpha = logo.split()[3]

    solid = Image.new("RGB", logo.size, color)
    flattened = Image.new("RGB", logo.size, (0, 0, 0))
    flattened.paste(solid, mask=alpha)
    return flattened


class AteezDisplay:
    def __init__(self, matrix):
        self.matrix = matrix

        emblem = _load_logo(EMBLEM_PATH, matrix.height, EMBLEM_COLOR)
        wordmark = _load_logo(WORDMARK_PATH, matrix.height, WORDMARK_COLOR)

        self.group_width = emblem.width + LOGO_GAP + wordmark.width
        self.group = Image.new("RGB", (self.group_width, matrix.height), (0, 0, 0))
        self.group.paste(emblem, (0, 0))
        self.group.paste(wordmark, (emblem.width + LOGO_GAP, 0))

    def run(self, duration=None):
        """Scroll the emblem and wordmark together, left to right, on a loop.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed (mid-scroll if need be).
        """
        deadline = time.monotonic() + duration if duration is not None else None

        canvas = self.matrix.CreateFrameCanvas()
        x = -self.group_width

        while deadline is None or time.monotonic() < deadline:
            x += 1
            if x > canvas.width:
                x = -self.group_width

            canvas.Clear()
            canvas.SetImage(self.group, x, 0)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(SCROLL_SPEED)

from PIL import Image, ImageSequence

import time

GIF_PATH = "assets/soccer_player_kicking.gif"
DEFAULT_FRAME_DURATION = 0.1  # seconds; fallback for frames with no/zero duration


class SoccerAnimDisplay:
    def __init__(self, matrix):
        self.matrix = matrix
        self.frames = self._load_frames(matrix.width, matrix.height)

    @staticmethod
    def _load_frames(panel_width, panel_height):
        gif = Image.open(GIF_PATH)

        scale = panel_height / gif.height
        frame_width = round(gif.width * scale)
        frame_height = round(gif.height * scale)
        x = (panel_width - frame_width) // 2
        y = (panel_height - frame_height) // 2

        frames = []
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert("RGBA").resize((frame_width, frame_height), Image.LANCZOS)

            # Flatten onto black in case any frames do have transparency.
            canvas_frame = Image.new("RGB", (panel_width, panel_height), (0, 0, 0))
            canvas_frame.paste(rgba, (x, y), mask=rgba.split()[3])

            duration = frame.info.get("duration", 0) / 1000
            frames.append((canvas_frame, duration or DEFAULT_FRAME_DURATION))

        return frames

    def run(self, duration=None):
        """Loop the soccer animation, centered on the panel.

        Runs forever if duration is None, otherwise stops once duration
        seconds have elapsed (mid-loop if need be).
        """
        deadline = time.monotonic() + duration if duration is not None else None

        canvas = self.matrix.CreateFrameCanvas()

        while deadline is None or time.monotonic() < deadline:
            for frame, frame_duration in self.frames:
                if deadline is not None and time.monotonic() >= deadline:
                    return

                canvas.SetImage(frame, 0, 0)
                canvas = self.matrix.SwapOnVSync(canvas)
                time.sleep(frame_duration)

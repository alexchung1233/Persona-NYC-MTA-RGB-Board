from itertools import cycle

from matrix_factory import create_matrix
from views.mta_display import MtaDisplay
from views.knicks_display import KnicksDisplay
from views.soccer_anim_display import SoccerAnimDisplay

MTA_DURATION = 5 * 60  # seconds of MTA train times between interludes
INTERLUDE_DURATION = 10  # seconds each interlude animation plays

matrix = create_matrix()
mta_display = MtaDisplay(matrix)

# Add more display classes here to rotate them in as interludes.
interludes = cycle([
    SoccerAnimDisplay(matrix),
    KnicksDisplay(matrix),
])

try:
    while True:
        mta_display.run(duration=MTA_DURATION)
        next(interludes).run(duration=INTERLUDE_DURATION)
except KeyboardInterrupt:
    matrix.Clear()

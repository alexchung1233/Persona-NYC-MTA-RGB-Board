from matrix_factory import create_matrix
from mta_display import MtaDisplay
from knicks_display import KnicksDisplay

MTA_DURATION = 5 * 60  # seconds of MTA train times between Knicks interludes
KNICKS_DURATION = 10  # seconds of Knicks scroll per interlude

matrix = create_matrix()
mta_display = MtaDisplay(matrix)
knicks_display = KnicksDisplay(matrix)

try:
    while True:
        mta_display.run(duration=MTA_DURATION)
        knicks_display.run(duration=KNICKS_DURATION)
except KeyboardInterrupt:
    matrix.Clear()

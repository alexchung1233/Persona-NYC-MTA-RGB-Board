from matrix_factory import create_matrix
from views.clock_display import ClockDisplay

matrix = create_matrix()
display = ClockDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

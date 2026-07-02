from matrix_factory import create_matrix
from views.knicks_display import KnicksDisplay

matrix = create_matrix()
display = KnicksDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

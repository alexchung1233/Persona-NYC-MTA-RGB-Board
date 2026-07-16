from matrix_factory import create_matrix
from views.ateez_display import AteezDisplay

matrix = create_matrix()
display = AteezDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

from matrix_factory import create_matrix
from mta_display import MtaDisplay

matrix = create_matrix()
display = MtaDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

from matrix_factory import create_matrix
from soccer_anim_display import SoccerAnimDisplay

matrix = create_matrix()
display = SoccerAnimDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

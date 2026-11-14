from matrix_factory import create_matrix
from views.weather_display import WeatherDisplay

matrix = create_matrix()
display = WeatherDisplay(matrix)

try:
    display.run()
except KeyboardInterrupt:
    matrix.Clear()

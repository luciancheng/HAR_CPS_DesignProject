# HAR parameters
SAMPLE_RATE=25 # Hz
WINDOW_SIZE=2 # seconds
WINDOW_OVERLAP=0 # seconds

# Classes
CLASS_A = 0 # standing
CLASS_B = 1 # sitting
CLASS_C = 2 # laying
CLASS_D = 3 # spinning CW

# Colours
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
PURPLE = [255, 0, 255]

CLASS_TO_COLOUR = {
    CLASS_A: RED, # standing
    CLASS_B: GREEN, # sitting
    CLASS_C: BLUE, # laying
    CLASS_D: YELLOW # spinning CW

}
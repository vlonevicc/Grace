#sudo pip3 install adafruit-circuitpython-dotstar
#sudo pip3 install adafruit-blinka


import random
import time
import threading
import board
import adafruit_dotstar as dotstar

# Settings
COLS = 16           
ROWS = 8            
TOTAL_LEDS = 128   
FPS_DELAY  = 0.03   # how long to wait between each frame (roughly 30fps)

COLOR_OFF       = (0,   0,   0)      # off
COLOR_TALKING   = (255, 100, 180)    # pink 4 talking
COLOR_LISTENING = (180, 0,   255)    # purple 4 listening


TARGET_INTERVAL = 0.12  # How often the bars pick a new random target height 

# Set up 4 the LED panels
dots = dotstar.DotStar(board.SCK, board.MOSI, TOTAL_LEDS, brightness=0.2)
         #board.SCK = clock pin, board.MOSI = data pin
         #128 = total number of LEDs, brightness = how bright (keep low to avoid overheating)



mode = "idle"
running = False  # controls animation thread 


# random bar heights for mouth movements
def get_random_heights():
    half_heights = []
    current_value = random.uniform(2, 7)

    for i in range(COLS // 2):
        current_value = current_value + random.uniform(-3, 3)

        if current_value < 0:
            current_value = 0
        if current_value > 8:
            current_value = 8

        half_heights.append(current_value)

    # Mirror left side to right side for symmetry
    right_side = half_heights[::-1]
    all_heights = half_heights + right_side

    return all_heights


# Glid bars 35% closer to their target every frame instead of jumping instantly
def move_bars_toward_target(current_heights, target_heights, speed=0.35):
    updated_heights = []

    for i in range(len(current_heights)):
        difference = target_heights[i] - current_heights[i]
        new_height = current_heights[i] + difference * speed
        updated_heights.append(new_height)

    return updated_heights


#  Build the LED grid from bar heights 
def build_grid(bar_heights, led_color):
    grid = []
    for row in range(ROWS):
        grid_row = []
        for col in range(COLS):
            grid_row.append(COLOR_OFF)
        grid.append(grid_row)

    center_row = ROWS // 2

    for col in range(COLS):
        height = int(round(bar_heights[col]))
        half_height = height // 2
        remainder = height % 2

        top_row    = center_row - half_height - remainder
        bottom_row = center_row + half_height

        for row in range(ROWS):
            if top_row <= row <= bottom_row:
                grid[row][col] = led_color

    return grid


#  Send the grid panels 
def send_to_panels(grid):
    led_index = 0

    for row in range(ROWS):
        for col in range(COLS):
            dots[led_index] = grid[row][col]
            led_index += 1
    dots.show()


#  Turn all LEDs off 
def clear_panels():
    dots.fill(COLOR_OFF)
    dots.show()




#  Animation loop that runs in its own thread ( runs in the background while Grace is speaking)
def animation_loop():
    global running, mode
 
    bar_heights    = [0.0] * COLS
    target_heights = [0.0] * COLS
    last_target_time = time.time()
 
    while running:
        current_time = time.time()
 
        if mode == "talking":
            if current_time - last_target_time >= TARGET_INTERVAL:
                target_heights = get_random_heights()
                last_target_time = current_time
            led_color = COLOR_TALKING
 
        elif mode == "listening":
            target_heights = [0.0] * COLS
            led_color = COLOR_LISTENING
 
        else:
            target_heights = [0.0] * COLS
            led_color = COLOR_OFF
 
        bar_heights = move_bars_toward_target(bar_heights, target_heights)
        grid = build_grid(bar_heights, led_color)
        send_to_panels(grid)
 
        time.sleep(FPS_DELAY)
 
    # When the loop ends, turn off all LEDs cleanly

    clear_panels()




#  to start the animation thread
def start_mouth():
    global running
    running = True
    thread = threading.Thread(target=animation_loop)
    thread.daemon = True    # thread stops automatically if main program stops
    thread.start()
    print("Mouth display started")
 
 
# for listening mode 
def set_listening():
    global mode
    mode = "listening"
 
 
# for talking mode
def set_talking():
    global mode
    mode = "talking"
 
 
# to turn off
def stop_mouth():
    global running
    running = False
    time.sleep(0.1)     
    clear_panels()
    print("Mouth display stopped")
 
 
#  For testing purposes: before connecting to speach pipeline (uncomment when ready.. still waiting on that jestson lol)
# if __name__ == "__main__":
#     print("Testing mouth display...")
#     print("Watch the panels - starting in listening mode for 3 seconds")
 
#     start_mouth()
#     set_listening()
#     time.sleep(3)
 
#     print("Switching to talking mode for 5 seconds")
#     set_talking()
#     time.sleep(5)
 
#     print("Stopping...")
#     stop_mouth()

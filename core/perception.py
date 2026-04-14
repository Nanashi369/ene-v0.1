import pyautogui
import time

last_position = pyautogui.position()
last_move_time = time.time()

def detect_user_activity():
    global last_position, last_move_time

    current_position = pyautogui.position()

    # se o mouse mexeu
    if current_position != last_position:
        last_position = current_position
        last_move_time = time.time()
        return "active"

    # se está parado há muito tempo
    idle_time = time.time() - last_move_time

    if idle_time > 10:
        return "idle"

    return "walk_1"
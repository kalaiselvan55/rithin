import time
import threading
from pynput import keyboard
import pyautogui

# --- Settings ---
CLICKS_PER_SECOND = 100         # change this if you want it faster/slower
SAFE_START_DELAY_SEC = 3       # small delay before first click when starting
# ----------------

click_interval = 1.0 / CLICKS_PER_SECOND
running = False
stop_event = threading.Event()
target_pos = None  # (x, y). If None, will click at current mouse position.


def click_loop():
    global running
    time.sleep(SAFE_START_DELAY_SEC)  # short grace period
    while running and not stop_event.is_set():
        # If no fixed target, click wherever the cursor is
        if target_pos is None:
            pyautogui.click()
        else:
            pyautogui.click(target_pos[0], target_pos[1])
        time.sleep(click_interval)


def on_press(key):
    global running, target_pos
    try:
        if key == keyboard.Key.f6:           # START
            if not running:
                running = True
                stop_event.clear()
                threading.Thread(target=click_loop, daemon=True).start()
                print("[START] Auto-clicking...")
        elif key == keyboard.Key.f7:         # STOP
            if running:
                running = False
                stop_event.set()
                print("[STOP] Auto-clicking paused.")
        elif key == keyboard.Key.f8:         # SET TARGET = current mouse pos
            target_pos = pyautogui.position()
            print(f"[TARGET] Will click at fixed position: {target_pos}")
        elif key == keyboard.Key.f9:         # CLEAR TARGET = follow cursor
            target_pos = None
            print("[TARGET] Cleared. Will click at current cursor location.")
        elif key == keyboard.Key.esc:        # EXIT
            print("[EXIT] Goodbye!")
            running = False
            stop_event.set()
            return False
    except Exception as e:
        print("Error:", e)


print("""
Auto Clicker Controls:
  F6 = Start
  F7 = Stop
  F8 = Set target to current mouse position
  F9 = Clear target (follow cursor)
  ESC = Quit

Tips:
- Keep the terminal visible at first; there’s a 3s safety delay on start.
- To slow down/speed up, change CLICKS_PER_SECOND at the top.
""")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

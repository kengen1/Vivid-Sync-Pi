import time
from rpi_ws281x import *
from flask import Flask, request, jsonify
import threading
from datetime import datetime, timedelta
import pytz

# Define the number of rows and LEDs per row
NUM_ROWS = 16
LEDS_PER_ROW = 73
TOTAL_LEDS = NUM_ROWS * LEDS_PER_ROW
LEDS_PER_ROW_TO_TARGET = 16

hex_values = [
    # Add your hex color values here
]

etime = None

thread_lock = threading.Lock()

# Initialize an empty 2D array
array_2d = []

# LED strip configuration:
LED_COUNT = TOTAL_LEDS  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 20  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45, or 53

# Initialize the library (must be called once before other functions).
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def reset_leds():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# Initialize all LEDs to off (black)
reset_leds()

def stop_led_display():
    global led_thread_running
    with thread_lock:
        if led_thread_running:
            led_thread_running = False
            reset_leds()
            print("LED display stopped.")

# Function to refresh the 2D array based on the hex_values
def refresh_array_2d():
    global array_2d
    array_2d = []
    for i in range(0, len(hex_values), 16):
        row = hex_values[i:i + 16]
        array_2d.append(row)

# Refresh array_2d initially
refresh_array_2d()

# Function to update hex_values array and restart LED display loop
def update_hex_values(new_hex_values):
    global hex_values, led_thread_running
    hex_values = new_hex_values
    refresh_array_2d()
    if not led_thread_running:
        start_led_display()

def is_etime_passed():
    global etime
    if etime is None:
        return False

    try:
        # Try to parse etime assuming it is in 24-hour format
        etime_obj = datetime.strptime(etime, '%H:%M').time()
    except ValueError:
        try:
            # If parsing fails, try to parse etime assuming it is in 12-hour format
            etime_obj = datetime.strptime(etime, '%I:%M %p').time()
        except ValueError:
            print("Invalid etime format. Expected format: 'HH:MM' or 'hh:mm AM/PM'")
            return False

    # Get the current time in AEST timezone
    current_time_aest = datetime.now(pytz.timezone('Australia/Sydney')).time()

    if current_time_aest >= etime_obj:
        etime = None  # Reset etime after it's passed
        return True
    return False
    
# Create a thread for LED display
led_thread_running = False
def start_led_display():
    global led_thread_running
    with thread_lock:
        if not led_thread_running:
            led_thread_running = True
            led_thread = threading.Thread(target=led_display)
            led_thread.start()

def led_display():
    global led_thread_running
    start_column = 0
    while led_thread_running:
        if is_etime_passed():
            reset_leds()
            led_thread_running = False
            print("etime passed, LEDs reset.")
            break
        # Set the LEDs in the current range to the corresponding color from the 2D array
        for row in range(NUM_ROWS):
            for col in range(LEDS_PER_ROW_TO_TARGET):
                actual_col = (start_column + col) % LEDS_PER_ROW
                index = row * LEDS_PER_ROW + actual_col
                hex_color = array_2d[row][col % len(array_2d[row])]  # Get the hex color value from the array
                r, g, b = tuple(int(hex_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))  # Parse hex to RGB
                strip.setPixelColor(index, Color(r, g, b))  # Set color

        strip.show()
        time.sleep(0.5)  # Delay for visibility

        # Clear the LEDs in the current range
        for row in range(NUM_ROWS):
            for col in range(LEDS_PER_ROW_TO_TARGET):
                actual_col = (start_column + col) % LEDS_PER_ROW
                index = row * LEDS_PER_ROW + actual_col
                strip.setPixelColor(index, Color(0, 0, 0))  # Set color to off

        start_column = (start_column + 1) % LEDS_PER_ROW

    led_thread_running = False

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    global etime
    data = request.json
    print(f"Received data: {data}")

    # Extract and update the hex values from the received data
    if 'message' in data:
        new_hex_values = data['message']
        update_hex_values(new_hex_values)
        
    if 'etime' in data:
        etime = data['etime']
        print(f"etime updated to: {etime}")

    stop_led_display()
    start_led_display()

    return jsonify({"message": "Data received successfully!"}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)

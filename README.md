# LED Control Server with Flask

This project is a Flask-based server designed to control LED displays using WS281x LED strips. It provides a REST API to receive LED colour values and a timer (`etime`) to manage the display. The server runs on a Raspberry Pi and controls the LEDs by updating their colours based on the received hex colour values.

## Features

- **Dynamic LED Display Control**: Update LED colours in real-time through a REST API.
- **Time-based LED Display Reset**: Automatically turns off the LED display at a specified time.
- **Flexible colour Configuration**: Allows dynamic updates of LED colours via hex colour values.

## Dependencies

- Flask
- rpi_ws281x
- pytz

Ensure you have Python 3 installed on your Raspberry Pi. This project uses the rpi_ws281x library for controlling WS281x LED strips and Flask for setting up the server.

## Installation

1. Clone this repository to your Raspberry Pi.
2. Install the required libraries:

    ```bash
    pip install flask rpi_ws281x pytz
    ```

3. Setup your LED strip by connecting it to the Raspberry Pi GPIO pin 18.

## Configuration

Before running the server, you may want to adjust the following variables in the code to match your LED strip setup:

- `NUM_ROWS`: Number of LED rows.
- `LEDS_PER_ROW`: LEDs per row.
- `LED_PIN`: The GPIO pin connected to the LED strip.
- `LED_BRIGHTNESS`: Brightness level (0-255).

## Running the Server

To start the server, run:

  ```bash
    python path/to/your/script.py
  ```

This will start the Flask server on port 3000, allowing it to receive POST requests with LED colour values and etime.

## API Endpoints

- **POST /data**: Updates the hex colour values for the LEDs and the `etime` (optional) when the display should reset. Expect a JSON payload with `message` (array of hex colour values) and `etime` (string, optional).

- **GET /ping**: Health check endpoint to verify the server is running.

Example POST request to `/data`:

  ```json
    {
      "message": ["#FF0000", "#00FF00", "#0000FF"],
      "etime": "22:30"
    }
  ```

## Contributing

Feel free to fork this project and submit pull requests with new features or improvements.

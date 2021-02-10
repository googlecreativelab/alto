# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import queue
import time

import RPi.GPIO as GPIO
import picamera
import pigpio

from button_handler import ButtonHandler
import imprint_engine
import servo_handler
import task
import ui


# Configuration for all the pins. The pin numbering used is BCM.
BUTTON_PINS = [5, 6]
LED_PIN = 16

# Servos are controlled by periodically sending a pulse. The length
# of the pulse sets the position. Typically servos accept a pulse length
# between 1ms and 2ms, although most can go beyond these limits to provide
# an increased range of motion.
# WARNING: changing the pulse lengths below 1ms or above 2ms may cause damage
# to a servo - please experiment carefully.
SERVO_CFG = [
        # The left hand servo is configured as a mirror image (start and
        # stop are switched around).
        dict(pin=24, start_pulse=0.00185, end_pulse=0.00115),
        # The right hand servo is configured normally.
        dict(pin=25, start_pulse=0.00115, end_pulse=0.00185),
]

# The minimum confidence to accept when classifying.
# This value must be between 0 and 1. A smaller value makes the system more
# likely to match any label, resulting in greater sensitivity.
CONFIDENCE = 0.8

# The classifying results are passed through a filter to produce more stable
# results.
# This value adjusts how quickly the unit responds to changes while
# classifying.
# This value must be between 0 and 1.
RESPONSIVENESS = 0.2


def set_up_led(bus, pin):
    '''Sets up the status LED.

    Args:
      bus: The message bus to bind to.
      pin: The GPIO pin to use.

    Returns:
      A set function to directly set the LED.

    Binds to:
        Output.set_led(value: float)

    Uses RPi.GPIO rather than pigpio so that an error can be displayed
    if the pigpio daemon is not running.
    '''
    GPIO.setup(pin, GPIO.OUT)

    def set(value):
        GPIO.output(pin, value >= 0.5)

    bus.bind('Output.set_led', set)
    return set


def set_up_buttons(bus, pins):
    '''Sets up the input buttons.

    Args:
      bus: The message bus to bind to.
      pins: A list of GPIO pins to use.

    Emits:
      Input.button_changed(index: int, pressed: bool)

    Uses pigpiod to provide debouncing.
    '''
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError('Pigpio failed to connect to the daemon')

    # Set up each pin with a pullup and a 500us glitch filter
    # for debouncing.
    for pin in pins:
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_UP)
        pi.set_glitch_filter(pin, 500)

    # Wait for the pins to settle.
    time.sleep(0.01)

    # Set up a callback to handle press/release events.
    def on_change(gpio, level, tick):
        idx = pins.index(gpio)
        bus.emit('Input.button_changed', idx, level == 0)

    for pin in pins:
        pi.callback(pin, pigpio.EITHER_EDGE, on_change)


def main(confidence=CONFIDENCE, responsiveness=RESPONSIVENESS):
    '''Runs all the tasks required for Alto.

    Uses a TaskManager to start the tasks, check that they are alive
    and as a messaging bus.

    Blinks the LED on any errors.

    Emits:
      System.started()
    '''
    task_manager = task.TaskManager()
    GPIO.setmode(GPIO.BCM)

    # Set up the LED first as it is used if there are any errors.
    set_led = set_up_led(task_manager, LED_PIN)

    try:
        # Start the output tasks first and input tasks last.
        # This should ensure that all the bindings are in place
        # before the inputs are processed.
        task_manager.start(imprint_engine.ImprintEngineTask,
                confidence, responsiveness)
        task_manager.start(servo_handler.ServoHandler, SERVO_CFG)
        task_manager.start(ui.AltoUI)
        task_manager.start(ButtonHandler)
        set_up_buttons(task_manager, BUTTON_PINS)

        # Indicate the system is ready by turning on the LED.
        task_manager.emit('System.started')
        set_led(1)

        # Run forever
        task_manager.process_messages()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logging.exception('Error in main')

        # Emit a blink error code
        if isinstance(exc,  picamera.PiCameraError):
            # Camera problems are shown as two blinks.
            blinks = 2
        else:
            # All other problems (most likely the TPU isn't conencted)
            # are shown as three blinks.
            blinks = 3

        set_led(0)
        time.sleep(1)
        # Emit the pattern 10 times.
        for _ in range(10):
            for _ in range(blinks):
                set_led(1)
                time.sleep(0.15)
                set_led(0)
                time.sleep(0.10)
            # Pause between sets.
            time.sleep(0.5)
    finally:
        # Clean up the tasks and turn the LED off on exit.
        task_manager.terminate()
        set_led(0)
        GPIO.cleanup()


if __name__ == "__main__":
    # Parse command line arguments.
    def norm_float(value):
        v = float(value)
        if v < 0 or v > 1:
            raise argparse.ArgumentTypeError(
                    '%s is not in the range of 0-1' % value)
        return v

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("--confidence", type=norm_float, default=CONFIDENCE,
            help='''
Sets the minimum confidence to accept when classifying.
This value must be between 0 and 1. A smaller value makes the system more
likely to match any label, resulting in greater sensitivity.''')

    parser.add_argument("--responsiveness", type=norm_float,
            default=RESPONSIVENESS,
            help='''
Sets how quickly the unit responds to changes while classifying.
This value must be between 0 and 1.''')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    main(args.confidence, args.responsiveness)

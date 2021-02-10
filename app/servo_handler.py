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

import math
import time

import pigpio

import task


class Servo(object):
    '''Keeps information about a servo.'''

    def __init__(self, pin, offset, scale):
        '''Constructor.

        Args:
          pin: int, the BCM pin number the servo is connected to.
          offset: float, the pulse length in seconds to use at position 0.
          scale: float, the amount to adjust the pulse length as position 1.'''
        self.pin = pin
        self.offset_us = offset * 1000000
        self.scale_us = scale * 1000000
        self.pulse_us = 0

    def set_position(self, value):
        '''Sets pulse_us using the given value.

        Args:
          value: Union[float, None], a normalised (0-1) input value.

        If the value is None then pulse_us is set to 0, which lets a
        servo idle.'''
        if value is None:
            self.pulse_us = 0
        else:
            value = max(0, min(1, value))
            self.pulse_us = int(self.offset_us + self.scale_us*value)


class ServoHandler(task.Task):
    '''Controls a number of servos.

    Binds to:
      Output.set_servo(index: int, value: float)
      Output.sweep_servos(duration: float, sweps: List([int, float, float]))

    Avoids power spikes by interleaving servo movements.
    Avoids jitter by idling after a configurable period of inactivity.
    '''

    # A common servo standard is to send pulses at 50Hz which is every 0.02
    # seconds.
    FRAME_PERIOD_US = 20000

    def __init__(self, task_args, config, drive_time=2):
        '''Constructor.

        Args:
          config: Tuple[Tuple[int, float, float]], the servos to use.
          drive_time: float, the time in seconds to drive the servos for.
        '''
        super().__init__(task_args)
        self.drive_time = drive_time
        self.last_change = time.monotonic()

        # Connect to pigpio.
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError('Pigpio failed to connect to the daemon')

        # Add all the servos.
        self.servos = []
        for item in config:
            self.add(**item)

        self.bind('Output.set_servo', self.set_servo)
        self.bind('Output.sweep_servos', self.sweep_servos)

    def run(self):
        '''The task's main loop.

        Processes messages and sends pulses.'''
        while self.process_messages(batch=True, block=self._is_idle()):
            if not self._is_idle():
                # Send the pulses to the servos.
                # To reduce CPU usage sends batches of 5 pulses at a time.
                self._send_pulses(self._get_pulses(), 5)

    def add(self, pin, start_pulse=0.001, end_pulse=0.002):
        '''Adds a servo with the supplied config.

        Args:
          pin: int, the BCM pin number the servo is connected to.
          start_pulse: float, the pusle length in seconds at position 0.
          end_pulse: float, the pusle length in seconds at position 1.
        '''
        # Set up the pin.
        self.pi.set_mode(pin, pigpio.OUTPUT)

        # Convert (start, end) to and (offset, scale) for easier maths.
        offset = start_pulse
        scale = end_pulse - start_pulse
        self.servos.append(Servo(pin, offset, scale))

    def set_servo(self, idx, value):
        '''Sets a servos position.

        Args:
          idx: int, the servo index.
          value: float, the position between 0 and 1.'''
        # Update the servo.
        servo = self.servos[idx]
        self.servos[idx].set_position(value)

        # Trigger driving.
        self.last_change = time.monotonic()

    def sweep_servos(self, duration, sweeps):
        '''Sweeps any number of servos in parallel.

        Args:
          duration: float, the time in seconds to sweep over.
          sweeps: List[Sweep], the sweeps to perform.

        Each item in the list of sweeps is a tuple of:
          (idx, start, end)

          idx is the servo index,
          start and end are normalised positions (0-1)
          duration is in seconds.

        This message is blocking.
        '''
        duration_us = duration * 1000000

        # Round up to the next frame period.
        frame_us = self.FRAME_PERIOD_US
        duration_us = int(math.ceil(duration_us/frame_us)*frame_us)

        # Build up a complete set of pulses for the entire duration
        pulses = []
        for us in range(0, duration_us, frame_us):
            norm_pos = us / (duration_us - frame_us)
            for idx, start, end in sweeps:
                self.servos[idx].set_position(start + (end-start) * norm_pos)
            pulses += self._get_pulses()

        # Send the pulses.
        self._send_pulses(pulses)

        # Trigger the idle logic.
        self.last_change = time.monotonic()

    def _is_idle(self):
        '''Returns True if the servos should be idle.'''
        return time.monotonic() > self.last_change + self.drive_time

    def _get_pulses(self):
        '''Gets the list of pulse instructions to send to pigpio.

        The instructions are for one pulse per servo.
        The pulses are interleaved to reduce peak power draw.
        '''
        count = len(self.servos)
        frame_duration = self.FRAME_PERIOD_US // count
        pulses = []
        for servo in self.servos:
            # Handle zero pulse widths specially, otherwise pigpio sends
            # single microsecond signals on the pin.
            if servo.pulse_us:
                # Pulses use a bitwise pin mask rather than a single pin.
                pin_mask = 1 << servo.pin
                pulses += [
                    # Turn on for the pulse time.
                    pigpio.pulse(pin_mask, 0, servo.pulse_us),
                    # Turn off for the rest of the frame.
                    pigpio.pulse(0, pin_mask, frame_duration - servo.pulse_us),
                ]
            else:
                pulses += [
                    # Do nothing for the entire frame.
                    pigpio.pulse(0, 0, frame_duration),
                ]
        return pulses

    def _send_pulses(self, pulses, repeat=1):
        '''Sends a list of pulses a number of times.

        Args:
          pulses: result of _get_pulses().
          repeat: int, the number of times to send the pulses.'''
        # Create a pi wave.
        self.pi.wave_add_generic(pulses)
        duration = (self.pi.wave_get_micros() / 1000000) * (repeat)
        wave = self.pi.wave_create()

        try:
            # Send the pi wave using the programmable chain method.
            self.pi.wave_chain([
                255, 0, # Loop start.
                wave,
                255, 1, repeat & 0xff, repeat >> 8, # Repeat repeat times.
            ])

            # Process messages for the entire duration.
            self.process_messages(duration)

            # Process messages while the wave completes.
            while self.pi.wave_tx_at() == wave:
                self.process_messages(self.FRAME_PERIOD_US / 1000000 / 2)
        finally:
            # Release the pi wave.
            self.pi.wave_delete(wave)

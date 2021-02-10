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

import time

import task


class ButtonHandler(task.Task):
    '''Processes low level input events from two buttons.

    Binds to:
      Input.button_changed(index: int, pressed: bool)

    Emits:
      ButtonHandler.single_button_pressed(index: int)
      ButtonHandler.both_buttons_pressed(pressed: bool)

    A single_button_pressed event is emitted when a button is pressed and either
      a: released
      b: held for longer than HOLD_THRESHOLD
    without the other button being pressed.

    A both_buttons_pressed(True) event is emitted when a button is pressed while
    the other button is also currently pressed.
    A both_buttons_pressed(False) event is then emitted when one of the
    buttons is released.
    '''

    # Time (in seconds) a button is held before being considered pushed.
    HOLD_THRESHOLD = 0.2

    # States
    IDLE = 0
    SINGLE_PUSH = 1
    DOUBLE_PUSH = 2
    WAITING_FOR_RELEASE = 3

    def __init__(self, task_args):
        super().__init__(task_args)
        self.state = self.IDLE
        self.buttons = [False, False]
        self.pushed_time = None

        self.bind('Input.button_changed', self.on_change)

    def on_change(self, idx, state):
        '''Call when a button changes.'''
        # Do nothing if the state has not changed.
        if self.buttons[idx] == state:
            return

        # Record the new button state.
        self.buttons[idx] = state

        if state:
            # Handle a button press.
            if self.state == self.IDLE:
                self.state = self.SINGLE_PUSH
                self.pushed_time = time.monotonic()
            elif self.state == self.SINGLE_PUSH:
                self.state = self.DOUBLE_PUSH
                self.emit('ButtonHandler.both_buttons_pressed', True)
        else:
            # Handle a button release..
            if self.state == self.SINGLE_PUSH:
                self.emit('ButtonHandler.single_button_pressed', idx)
                self.state = self.IDLE
            elif self.state == self.DOUBLE_PUSH:
                self.state = self.WAITING_FOR_RELEASE
                self.emit('ButtonHandler.both_buttons_pressed', False)
            elif self.state == self.WAITING_FOR_RELEASE:
                if not (self.buttons[0] or self.buttons[1]):
                    self.state = self.IDLE

    def run(self):
        '''The task's main loop.

        Processes messages and handles buttons being pushed and held.'''
        def get_duration():
            '''Gets the duration to process messages for.

            Duration is None (forever) unless the HOLD_THRESHOLD test needs to
            be run.'''
            if self.state == self.SINGLE_PUSH:
                return self.HOLD_THRESHOLD - elapsed
            else:
                return None

        while self.process_messages(get_duration(), batch=True):
            if self.state == self.SINGLE_PUSH:
                # Perform the check for a single held push.
                elapsed = time.monotonic() - self.pushed_time
                if elapsed >= self.HOLD_THRESHOLD:
                    # A button has been held for long enough to consider it
                    # pushed.
                    idx = 0 if self.buttons[0] else 1
                    self.emit('ButtonHandler.single_button_pressed', idx)
                    self.state = self.WAITING_FOR_RELEASE

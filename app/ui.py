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

import logging
import time

import task


class BaseUI(task.Task):
    '''Base class for driving the user interaction.

    Processes messages and handles state. Calls functions to handle
    outputs which should be overloaded by a subclass.

    Binds to:
      ButtonHandler.single_button_pressed(index: int)
      ButtonHandler.both_buttons_pressed(pressed: bool)
      Engine.matched(label: Union[Any, None])
      System.started()'''

    IDLE = 0
    TRAINING = 1
    RESETTING = 2

    def __init__(self, task_args):
        '''Constructor.'''
        super().__init__(task_args)

        self.state = self.IDLE
        self.reset_released = True

        self.bind('ButtonHandler.single_button_pressed', self.on_training_event)
        self.bind('ButtonHandler.both_buttons_pressed', self.on_reset_event)

        self.bind('Engine.matched', self.on_match_event)

        self.bind('System.started', self.show_starting)

    def on_training_event(self, label):
        '''Called when training has been requested.

        Args:
          label: int, the button index to use as the label.'''
        if self.state == self.IDLE:
            # Run training.
            self.state = self.TRAINING
            self.run_training(label)

            # Ensure the engine is idle after training so no new match results
            # are emitted.
            self.call('Engine.idle')

            # Process messages while state is TRAINING to discard any queued
            # match results.
            self.process_messages(block=False)

            # Start classifiying.
            self.state = self.IDLE
            self.emit('Engine.start_classifying')

    def on_reset_event(self, pressed):
        '''Called when a reset has been requested or released.

        Args:
          pressed: bool, the buttons have been pressed.'''
        if self.state == self.IDLE and pressed:
            self.state = self.RESETTING
            # Keep track of the button state, run_reset() might implement a
            # time threshold.
            self.reset_released = False
            self.run_reset()
            # Maintain the RESETTING state until the buttons are released.
        elif self.state == self.RESETTING and not pressed:
            self.reset_released = True
            self.state = self.IDLE

    def on_match_event(self, label):
        '''Called when the engine has detected a new match or loss of match.

        Args:
          label: Union[Any, None], the matched label, or None.'''
        if self.state == self.IDLE:
            self.show_match_result(label)

    # Methods to be overloaded.

    def show_starting(self):
        '''Called at startup.'''
        pass

    def show_match_result(self, label):
        '''Called when the match result changes.

        Args:
          label: Union[Any, None], the matched label, or None.'''
        pass

    def run_training(self, label):
        '''Called when training has been requested.

        Args:
          label: int, the button index to use as the label.'''
        pass

    def run_reset(self):
        '''Called when a reset has been requested.'''
        pass


class AltoUI(BaseUI):
    '''Class for driving the user interaction.

    Uses two servos as outputs to indicate state.'''

    def show_starting(self):
        '''Called at startup.'''
        logging.info('starting')
        self.emit('Output.set_servo', 0, 0)
        self.emit('Output.set_servo', 1, 0)

    def show_match_result(self, label):
        '''Called when the match result changes.

        Args:
          label: Union[Any, None], the matched label, or None.'''
        logging.info('show_match_result %s', label)
        self.emit('Output.set_servo', 0, 1 if label == 0 else 0)
        self.emit('Output.set_servo', 1, 1 if label == 1 else 0)

    def run_training(self, label):
        '''Called when training has been requested.

        Args:
          label: int, the button index to use as the label.'''
        logging.info('run_training %s', label)

        # Reset to the idle state.
        self.call('Engine.idle') # Block to ensure state sync.
        self.emit('Output.set_servo', 0, 0)
        self.emit('Output.set_servo', 1, 0)
        time.sleep(0.5)

        # Start learning and perform an animation.
        duration = 5
        self.call('Engine.start_learning', label) # Block to ensure state sync.
        self.emit('Output.sweep_servos', duration, [(label, 0, 1)])
        self.process_messages(duration)

        # Reset back to the idle state.
        self.call('Engine.idle') # Block to ensure state sync.
        self.emit('Output.set_servo', label, 0)
        time.sleep(0.5)

    def run_reset(self):
        '''Called when a reset has been requested.'''
        logging.info('run_reset')
        self.call('Engine.reset') # Block to ensure state sync.
        self.emit('Output.set_servo', 0, 0)
        self.emit('Output.set_servo', 1, 0)

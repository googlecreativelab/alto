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

import collections
import ctypes
import logging
import multiprocessing
import os
import queue
import threading
import time


Message = collections.namedtuple('Message', ['name', 'args', 'results'])
TaskInfo = collections.namedtuple('TaskInfo', ['cls', 'process'])


class TaskManager(object):
    '''Manages tasks running in subprocesses, and communication between them.

    The messaging bus allows any number of listeners to bind to a message,
    which is identified by a string. Either the process running the manager,
    or any of the tasks may 'emit' a message by name and can optionally
    supply arguments.

    Tasks may also 'call' a message which will block and return a list of
    results, one from each active binding to that message.'''

    def __init__(self):
        '''Constructor.'''
        # A List[TaskInfo] of all the started tasks.
        self.tasks = []
        # A single shared Queue for receiving messages from tasks.
        self.message_queue = multiprocessing.Queue()
        # A Map[String, Callable] of message names and thier bindings.
        self.bindings = collections.defaultdict(list)
        # A Map[pid, Connection] of process IDs and the connection used
        # to send messages to that task.
        self.senders = {}

        self.bind('TaskManager.bind', self.bind)
        self.bind('TaskManager.bind_task', self.bind_task)
        self.bind('TaskManager.start', self.start)

    def start(self, task_cls, *args):
        '''Starts a task.

        The task_cls is constructed in a subprocess, using args if provided.
        Its run method is then invoked.

        Args:
          task_cls: Task, the subclass of Task to run.
          args: Any, the arguments to be passed to the constructor.'''
        # Create a Pipe used for sending messages to this task.
        receiver, sender = multiprocessing.Pipe(False)

        # Use a shared value to determine when the Task has been constructed.
        # This can be used to ensure all bindings in the constructor have
        # been registered, an important consideration in start up order.
        constructed = multiprocessing.Value(ctypes.c_bool, lock=False)
        constructed_condition = multiprocessing.Condition()

        def run_task():
            '''Subprocess function.'''
            try:
                try:
                    # Construct the task instance.
                    task = task_cls((self.message_queue, receiver), *args)
                finally:
                    # Ensure that constructed is set before continuing.
                    with constructed_condition:
                        constructed.value = True
                        constructed_condition.notify()
                # Run the task forever.
                task.run()
            except KeyboardInterrupt:
                pass
            except Exception as exc:
                # Log any errors and also send them to the TaskManager.
                logging.exception(exc)
                self.message_queue.put(exc)

        # Create the new process.
        process = multiprocessing.Process(
                target=run_task, name=task_cls.__name__)
        process.start()
        logging.info('Task %s has pid %d', task_cls.__name__, process.pid)

        # Wait for construction to complete.
        with constructed_condition:
            while process.is_alive() and not constructed.value:
                constructed_condition.wait(2)

        if not process.is_alive():
            process.join()
            raise RuntimeError('Task {} stopped'.format(task_cls.__name__))

        # Store the task details.
        self.senders[process.pid] = sender
        self.tasks.append(TaskInfo(task_cls, process))

        return process.pid

    def bind(self, name, callback):
        '''Binds the named message to a callback.

        Args:
          name: String, the message name.
          callback: Callable, the method to be invoked.

        The callback will be invoked when the message is emitted or called.'''
        # This handler manages the sending of results if a results Connection
        # is specified.
        def handle_message(msg):
            result = callback(*msg.args)
            if msg.results:
                msg.results.send(result)
        self.bindings[name].append(handle_message)

    def bind_task(self, name, pid):
        '''Binds the named message to a task specified by process ID.

        Args:
          name: String, the message name.
          pid: int, the process ID of the task.

        When the message is emitted or called it will be forwarded to that
        task.

        This is used internally by Task.bind().'''
        send = self.senders[pid].send
        self.bindings[name].append(send)

    def emit(self, message_name, *args):
        '''Broadcasts a message to the bus.

        Args:
          name: String, the message name.
          args: Any, the arguments to be passed to the listeners.'''
        self.message_queue.put(Message(message_name, args, None))

    def process_messages(self):
        '''The main loop for a TaskManager.

        Reads incoming messages from the message queue and dispatches them
        according to any bindings.'''
        # Check that all the subprocesses are still alive at regular
        # intervals.
        alive_check_at = time.monotonic()
        while True:
            try:
                message = self.message_queue.get(timeout=5)
            except queue.Empty:
                pass
            else:
                logging.debug(message)
                if isinstance(message, Message):
                    # Dispatch the incoming message to any bound callbacks.
                    if message.name in self.bindings:
                        bindings = self.bindings[message.name]

                        # When a 'call' is made the message specifies a
                        # results Connection. The first item sent is the number
                        # of bindings, which is the number of results that will
                        # be sent as subsequent items.
                        if message.results:
                            message.results.send(len(bindings))

                        for sender in bindings:
                            sender(message)
                else:
                    # The message was an Exception, so raise it in this
                    # proceess.
                    raise message

            # The regular aliveness check.
            if time.monotonic() >= alive_check_at:
                for task_cls, process in self.tasks:
                    if not process.is_alive():
                        # The process exited / died, so join it and raise the
                        # issue.
                        process.join()
                        raise RuntimeError('Task {} stopped'.format(
                            task_cls.__name__))
                alive_check_at = time.monotonic() + 5

    def terminate(self):
        '''Terminates all the running tasks.'''
        for _, process in self.tasks:
            process.terminate()
            process.join()


class Task(object):
    '''A worker run in a subprocess that interacts with the message bus.

    A Task will often bind to messages on the bus. Because it is important
    to ensure all bindings are in place before other tasks invoke them, they
    must be set up in the constructor. The TaskManager waits for the
    constructor to finish before resuming its execution.'''

    def __init__(self, task_args):
        # The communication points are passed in a tuple for convenience.
        self.sender, self.receiver = task_args
        # A Map[String, Callable] of message names and thier bindings.
        self.bindings = {}

        # If setproctitle has been installed then this helps identify
        # which process is which task.
        try:
            import setproctitle
            setproctitle.setproctitle('alto ' + type(self).__name__)
        except:
            pass

    def bind(self, message_name, callback):
        '''Binds the named message to a callback.

        Args:
          name: String, the message name.
          callback: Callable, the method to be invoked.

        The callback will be invoked when the message is emitted or called.'''
        self.bindings[message_name] = callback
        # Instruct the TaskManager to forward messages to this task.
        self.emit('TaskManager.bind_task', message_name, os.getpid())

    def emit(self, message_name, *args):
        '''Broadcasts a message to the bus.

        Args:
          name: String, the message name.
          args: Any, the arguments to be passed to the listeners.'''
        # Send the message to the TaskManager, it will dispatch it.
        self.sender.put(Message(message_name, args, None))

    def call(self, message_name, *args):
        '''Broadcasts a message to the bus and return the results.

        Args:
          name: String, the message name.
          args: Any, the arguments to be passed to the listeners.

        Returns:
          List[Any], a result from every listener bound to the message.'''
        # Create a Pipe for receiving replies.
        receiver, sender = multiprocessing.Pipe(False)
        self.sender.put(Message(message_name, args, sender))
        # The TaskManager sends the number of bindings first.
        count = receiver.recv()
        # The rest of the items are the replies.
        return [receiver.recv() for _ in range(count)]

    def process_messages(self, duration=None, block=True, batch=False):
        '''Process messages sent by the TaskManager.

        Args:
          duration: Union[Float, None], the time in seconds to spend processing.
          block: bool, True if this call should block execution.
          batch: bool, True if this call should only process pending messages.

        Returns:
          False if the task should exit, otherwise True.

        If the duration is a float, then this call will return after at least
        duration seconds have elapsed.

        If block is False then this call will return after all pending
        messages have been processed.

        If batch is False then this call will process at least one message
        (subject to duration and block) and then return after all pending
        messages have been processed.'''
        # Keep track of the end time.
        end_at = None if duration is None else duration + time.monotonic()
        while True:
            if not block:
                # Use a non blocking poll.
                have_message = self.receiver.poll()
            elif end_at is None:
                # Use an infinite poll.
                have_message = self.receiver.poll(None)
            else:
                # Use a poll with a timeout.
                have_message = self.receiver.poll(end_at-time.monotonic())

            if not have_message:
                break

            msg = self.receiver.recv()

            # The TaskManager can send a None message to indicate shutdown.
            if msg is None:
                return False

            # Process this message, sending back results if requested.
            result = self.bindings[msg.name](*msg.args)
            if msg.results:
                msg.results.send(result)

            # At least one message has been processed, so stop blocking.
            if batch:
                block = False

        return True

    def run(self):
        '''The task's main loop.

        Processes messages forever.'''
        while True:
            self.process_messages(None)

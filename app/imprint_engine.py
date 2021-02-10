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
import logging

from edgetpu.basic import basic_engine
import numpy as np
import picamera

import task


log = logging.getLogger('imprint_engine')


class ImprintEngineTask(task.Task):
    '''Handles learning and classifying using machine learning.

    While learning or classifying the RPi camera is used to capture frames.
    These are then processed with the engine.

    Binds to:
      Engine.idle()
      Engine.start_learning(label: Any)
      Engine.start_classifying()
      Engine.reset()

    Emits:
      Engine.confidences(donfidences: Dict[Any, float])
      Engine.matched(label: Union[Any, None])'''

    # States
    IDLE = 0
    LEARNING = 1
    CLASSIFYING = 2

    # The tflite model to use.
    model_path = 'mobilenet_quant_v1_224_headless_edgetpu.tflite'

    # The input weight to use for the infinite impulse response filters.
    # This value must be between 0 and 1. A larger value gives more importance
    # to the newest results and less the the older results, resulting in greater
    # responsiveness (less stability).
    iir_weight = 0.2

    # The minimum confidence to accept when classifying.
    # This value must be between 0 and 1. A smaller value makes the system more
    # likely to match any label, resulting in greater sensitivity.
    confidence = 0.8

    def __init__(self, task_args, confidence=None, responsiveness=None):
        super().__init__(task_args)

        # Use confidence and responsiveness if specified.
        if confidence is not None:
            self.confidence = confidence
        if responsiveness is not None:
            self.iir_weight = responsiveness

        self.state = self.IDLE
        self.requested_state_change = None
        self.label = None # Used when start_learning is called.

        self.engine = KNNEmbeddingEngine(self.model_path)
        self.shape = self._get_shape()

        self.bind('Engine.idle', self.idle)
        self.bind('Engine.start_learning', self.start_learning)
        self.bind('Engine.start_classifying', self.start_classifying)
        self.bind('Engine.reset', self.reset)

    def run(self):
        '''The task's main loop.

        Processes messages and handles state changes.'''
        with picamera.PiCamera() as cam:
            # Directly capture at the input tensor resolution.
            cam.resolution = self.shape
            # This frame rate works well on an RPi zero.
            cam.framerate = 8
            # The camera is installed upside down.
            cam.rotation = 180
            # This setting helps reduce motion blur.
            cam.exposure_mode = 'sports'

            # Use a top level dispatch to avoid unbound nesting of calls.
            while True:
                if self.requested_state_change is not None:
                    # Jump to the most recent requested state.
                    self.state = self.requested_state_change
                    self.requested_state_change = None

                if self.state == self.LEARNING:
                    self._run_learning(cam, self.label)
                elif self.state == self.CLASSIFYING:
                    self._run_classifying(cam)
                elif not self.process_messages(batch=True):
                    break

    def idle(self):
        '''Stops learning / classifying.'''
        self.requested_state_change = self.IDLE

    def start_learning(self, label):
        '''Starts learning for the given label.

        Args:
          label: Any

        If there is already learning data for the given label then it is
        augmented with the new data.'''
        self.requested_state_change = self.LEARNING
        self.label = label

    def start_classifying(self):
        '''Starts classifying images from the camera.'''
        self.requested_state_change = self.CLASSIFYING

    def reset(self):
        '''Stops learning / classifying and resets all learning data.'''
        self.state = self.IDLE
        self.label = None
        self.engine.clear()

    def _get_shape(self):
        '''Returns the input tensor shape as (width, height).'''
        input_tensor_shape = self.engine.get_input_tensor_shape()
        return (input_tensor_shape[2], input_tensor_shape[1])

    def _get_emb(self, image):
        '''Returns the embedding vector for the given image.

        Args:
          image: numpy.array, a uint8 RGB image with the correct shape.'''
        return self.engine.RunInference(image.flatten())[1].copy()

    def _run_learning(self, cam, label):
        '''Performs a learning loop until the state changes.

        Args:
          cam: The RPi camera.
          label: Any, the label to use for the new data.'''
        log.info('learning started')
        # Use capture_continuous and the video port to stream camera data
        # into a numpy array.
        output = np.empty((self.shape[0], self.shape[1], 3), dtype=np.uint8)
        gen = cam.capture_continuous(output, format='rgb', use_video_port=True)
        for idx, _ in enumerate(gen):
            # Store this new embedding.
            self.engine.add_embedding(label, self._get_emb(output))
            # Process messages for a state change.
            if not self.process_messages(block=False):
                return
            if self.requested_state_change is not None:
                break
        log.info('learning stopped')

    def _run_classifying(self, cam):
        '''Performs a classifying loop until the state changes.

        Args:
          cam: The RPi camera.'''
        log.info('classifying started')

        # Maintain a map of labels to IIR filtered confidences.
        self.results = collections.defaultdict(
            lambda: InfiniteImpulseResponseFilter(self.iir_weight))

        # Track the label emitted with Engine.matched.
        current_label = None

        # Use capture_continuous and the video port to stream camera data
        # into a numpy array.
        output = np.empty((self.shape[0], self.shape[1], 3), dtype=np.uint8)
        gen = cam.capture_continuous(output, format='rgb', use_video_port=True)
        for _ in gen:
            # Use the engine to assess confidences.
            confidences = self.engine.get_confidences(self._get_emb(output))
            self.emit('Engine.confidences', confidences)
            log.debug('confidences = %s', confidences)

            # Update the filters.
            for label, confidence in confidences.items():
                self.results[label].update(confidence)

            # Find the label with the greatest confidence.
            match_label, iir = max(
                self.results.items(),
                key=lambda item: item[1].output)

            # If the confidence is not great enough then the match is None.
            if iir.output < self.confidence:
                match_label = None

            # If the match is different then emit the change.
            if match_label != current_label:
                current_label = match_label
                self.emit('Engine.matched', current_label)

                # Apply some hysteresis after every change, by resetting
                # the IIR filters either high (for the current label) or low.
                for label, iir in self.results.items():
                    iir.reset(1 if label == current_label else 0)

            # Process messages for a state change.
            if not self.process_messages(block=False):
                return
            if self.requested_state_change is not None:
                break

        # If there is a current_label then emit the change to None.
        if current_label is not None:
            self.emit('Engine.matched', None)

        log.info('classifying stopped')


class InfiniteImpulseResponseFilter(object):
    '''Filters an input over time.

    With every update the output is set to a portion (weight) of the current
    input value, combined with a portion (1-weight) of the previous output.'''

    def __init__(self, weight, value=0):
        '''Constructor.

        Args:
          weight: float, the weight (0-1) to give new inputs.
          value: float, the initial value.'''
        self.weight = weight
        self.output = value

    def update(self, input):
        '''Updates the output.

        Args:
          input: float, the current input.'''
        self.output *= (1 - self.weight)
        self.output += input * self.weight

    def reset(self, value=0):
        '''Resets the output.

        Args:
          value: float, the new output.'''
        self.output = value


class EmbeddingEngine(basic_engine.BasicEngine):
    '''Engine used to obtain embeddings from headless mobilenets.'''

    def __init__(self, model_path):
        '''Creates a EmbeddingEngine with given model.

        Args:
          model_path: str, path to a TF-Lite Flatbuffer file.

        Raises:
          ValueError: The model output is invalid.
        '''
        super().__init__(model_path)
        output_tensors_sizes = self.get_all_output_tensors_sizes()
        if output_tensors_sizes.size != 1:
            raise ValueError((
                'Dectection model should have only 1 output tensor!'
                'This model has {}.'.format(output_tensors_sizes.size)))


class KNNEmbeddingEngine(EmbeddingEngine):
    '''Extends embedding engine to provide kNearest Neighbor detection.

    This class maintains an in-memory store of embeddings and provides a
    function to get confidences of a query emedding using k nearest
    neighbors.
    '''

    def __init__(self, model_path, k_nearest_neighbors=3, maxlen=1000):
        '''Creates a EmbeddingEngine with given model.

        Args:
          model_path: String, path to TF-Lite Flatbuffer file.
          k_nearest_neighbors: int, the number of neighbors to use for
            confidences.
          maxlen: int, the maximum number of embeddings to store per label.

        Raises:
            ValueError: The model output is invalid.
        '''
        super().__init__(model_path)
        self.embedding_map = collections.defaultdict(list)
        self.knn = k_nearest_neighbors
        self.maxlen = maxlen

    def clear(self):
        '''Clear the store: forgets all stored embeddings.'''
        self.embedding_map = collections.defaultdict(list)

    def add_embedding(self, label, emb):
        '''Add an embedding vector to the store.'''
        # Normalize the vector.
        normal = emb / np.sqrt((emb**2).sum())

        # Add to store, under label.
        embeddings = self.embedding_map[label]
        embeddings.append(normal)

        # Discard if maxlen is exceeded.
        if len(embeddings) > self.maxlen:
            self.embedding_map[label] = embeddings[-self.maxlen:]

    def get_confidences(self, query_emb):
        '''Returns the match confidences for a query embedding.

        Args:
          query_emb: The embedding vector to match against.

        Returns:
          Dict[Any, float], a mapping of labels to match confidences.'''
        # Normalize the query embedding.
        query_emb = query_emb/np.sqrt((query_emb**2).sum())

        # Build up a dictionary of results, one for each label.
        results = {}

        for label, embeds in self.embedding_map.items():
            # Perform a matrix multiplication to get the cosine distance
            # from the stored embeddings. This distance is the confidence.
            dists = np.matmul(embeds, query_emb)

            if len(dists) <= self.knn:
                # Use all the confidences as the nearest neighbors.
                k_largest = dists
            else:
                # Use just the knn biggest confidences.

                # Partition performs a partial sort, making sure the index
                # (-self.knn) is correct and everything after is bigger.
                # This is cheaper than a full sort.
                k_largest = np.partition(dists, -self.knn)[-self.knn:]

            # The confidence for this label is the average of k_largest.
            results[label] = np.average(k_largest)

        return results

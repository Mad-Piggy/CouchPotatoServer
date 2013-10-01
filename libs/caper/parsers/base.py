# Copyright 2013 Dean Gardiner <gardiner91@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from logr import Logr
from caper import FragmentMatcher
from caper.group import CaptureGroup
from caper.result import CaperResult, CaperClosureNode


class Parser(object):
    def __init__(self, pattern_groups):
        self.matcher = FragmentMatcher(pattern_groups)

        self.closures = None
        #: :type: caper.result.CaperResult
        self.result = None

        self._match_cache = None
        self._fragment_pos = None
        self._closure_pos = None
        self._history = None

        self.reset()

    def reset(self):
        self.closures = None
        self.result = CaperResult()

        self._match_cache = {}
        self._fragment_pos = -1
        self._closure_pos = -1
        self._history = []

    def setup(self, closures):
        """
        :type closures: list of CaperClosure
        """

        self.reset()
        self.closures = closures

        self.result.heads = [CaperClosureNode(closures[0])]

    def run(self, closures):
        """
        :type closures: list of CaperClosure
        """

        raise NotImplementedError()

    #
    # Closure Methods
    #

    def next_closure(self):
        self._closure_pos += 1
        closure = self.closures[self._closure_pos]

        self._history.append(('fragment', -1 - self._fragment_pos))
        self._fragment_pos = -1

        if self._closure_pos != 0:
            self._history.append(('closure', 1))

        Logr.debug('(next_closure) closure.value: "%s"', closure.value)
        return closure

    def closure_available(self):
        return self._closure_pos + 1 < len(self.closures)

    #
    # Fragment Methods
    #

    def next_fragment(self):
        closure = self.closures[self._closure_pos]

        self._fragment_pos += 1
        fragment = closure.fragments[self._fragment_pos]

        self._history.append(('fragment', 1))

        Logr.debug('(next_fragment) closure.value "%s" - fragment.value: "%s"', closure.value, fragment.value)
        return fragment

    def fragment_available(self):
        if not self.closure_available():
            return False
        return self._fragment_pos + 1 < len(self.closures[self._closure_pos].fragments)

    def rewind(self):
        for source, delta in reversed(self._history):
            Logr.debug('(rewind) Rewinding step: %s', (source, delta))
            if source == 'fragment':
                self._fragment_pos -= delta
            elif source == 'closure':
                self._closure_pos -= delta
            else:
                raise NotImplementedError()

        self.commit()

    def commit(self):
        Logr.debug('(commit)')
        self._history = []

    #
    # Capture Methods
    #

    def capture_fragment(self, tag, regex=None, func=None, single=True):
        return CaptureGroup(self, self.result).capture_fragment(
            tag,
            regex=regex,
            func=func,
            single=single
        )

    def capture_closure(self, tag, regex=None, func=None, single=True):
        return CaptureGroup(self, self.result).capture_closure(
            tag,
            regex=regex,
            func=func,
            single=single
        )

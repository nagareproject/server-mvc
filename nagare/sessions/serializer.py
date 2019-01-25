# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

try:
    from cStringIO import StringIO as BuffIO
except ImportError:
    from io import BytesIO as BuffIO

from .exceptions import StateError


class DummyFile(object):
    """A write-only file that does nothing"""
    def write(self, data):
        pass


class Dummy(object):
    def __init__(self, pickler, unpickler):
        """Initialization

          - ``pickler`` -- pickler to use
          - ``unpickler`` -- unpickler to use
        """
        self.pickler = pickler
        self.unpickler = unpickler
        self.persistent_id = lambda o, clean_callbacks, callbacks, session_data, tasklets: None

    def _dumps(self, pickler, data, clean_callbacks):
        """Serialize an objects graph

        In:
          - ``pickler`` -- pickler to use
          - ``data`` -- the objects graph
          - ``clean_callbacks`` -- do we have to forget the old callbacks?

        Out:
          - data to keep into the session
          - data to keep into the state
        """
        session_data = {}
        tasklets = set()
        callbacks = {}

        # Serialize the objects graph and extract all the callbacks
        # pickler.inst_persistent_id = lambda o: persistent_id(o, clean_callbacks, callbacks, session_data, tasklets)
        pickler.persistent_id = lambda o: self.persistent_id(o, clean_callbacks, callbacks, session_data, tasklets)
        pickler.dump(data)

        return session_data, callbacks, tasklets

    def dumps(self, data, clean_callbacks):
        """Serialize an objects graph

        In:
          - ``data`` -- the objects graph
          - ``clean_callbacks`` -- do we have to forget the old callbacks?

        Out:
          - data kept into the session
          - data kept into the state
        """
        pickler = self.pickler(DummyFile(), protocol=-1)
        session_data, callbacks, tasklets = self._dumps(pickler, data, clean_callbacks)

        # This dummy serializer returns the data untouched
        return None, (data, callbacks)

    def loads(self, session_data, state_data):
        """Deserialize an objects graph

        In:
          - ``session_data`` -- data from the session
          - ``state_data`` -- data from the state

        Out:
          - the objects graph
          - the callbacks
        """
        return state_data


class Pickle(Dummy):
    def dumps(self, data, clean_callbacks):
        """Serialize an objects graph

        In:
          - ``data`` -- the objects graph
          - ``clean_callbacks`` -- do we have to forget the old callbacks?

        Out:
          - data kept into the session
          - data kept into the state
        """
        f = BuffIO()
        pickler = self.pickler(f, protocol=-1)
        # Pickle the data
        session_data, callbacks, tasklets = self._dumps(pickler, data, clean_callbacks)

        # Pickle the callbacks
        # pickler.inst_persistent_id = lambda o: None
        pickler.persistent_id = lambda o: None
        pickler.dump(callbacks)

        # Kill all the blocked tasklets, which are now serialized
        for t in tasklets:
            t.kill()

        # The pickled data are returned
        state_data = f.getvalue()

        f = BuffIO()
        self.pickler(f, protocol=-1).dump(session_data)
        session_data = f.getvalue()

        return session_data, state_data

    def loads(self, session_data, state_data):
        """Deserialize an objects graph

        In:
          - ``session_data`` -- data from the session
          - ``state_data`` -- data from the state

        Out:
          - the objects graph
          - the callbacks
        """
        p = self.unpickler(BuffIO(state_data))
        if session_data:
            session_data = self.unpickler(BuffIO(session_data)).load()
            p.persistent_load = lambda i: session_data.get(int(i))

        try:
            return p.load(), p.load()
        except Exception:
            raise StateError()

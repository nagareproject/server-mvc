# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from contextlib import contextmanager

from nagare.services import plugin
from nagare.session import set_session
from nagare.sessions import exceptions


class Session(object):
    def __init__(self, sessions_service, is_new, secure_token, session_id, state_id, use_same_state):
        self.sessions = sessions_service
        self.is_new = is_new
        self.secure_token = secure_token
        self.session_id = session_id
        self.state_id = state_id
        self.use_same_state = use_same_state

        self.data = {}

    def get_lock(self):
        return self.sessions.get_lock(self.session_id)

    def create(self):
        self.session_id, self.state_id, self.secure_token, lock = self.sessions.create(self.secure_token)
        return lock

    def fetch(self):
        if self.is_new:
            callbacks = {}
        else:
            new_state_id, self.secure_token, data = self.sessions.fetch(self.session_id, self.state_id)
            if not self.use_same_state:
                self.state_id = new_state_id
            self.data, callbacks = data

        return self.data, callbacks

    def store(self):
        self.sessions.store(self.session_id, self.state_id, self.secure_token, self.use_same_state, self.data)

    @contextmanager
    def enter(self):
        lock = self.create() if self.is_new else self.get_lock()

        with lock:
            yield self.fetch()
            self.store()


class SessionService(plugin.Plugin):
    LOAD_PRIORITY = 100
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        states_history='boolean(default=False)',

        session_cookie={
            'name': 'string(default="nagare-session")',
            'secure': 'boolean(default=False)',
            'httponly': 'boolean(default=True)',
            'max_age': 'integer(default=None)'
        },

        security_cookie={
            'name': 'string(default="nagare-token")',
            'secure': 'boolean(default=False)',
            'httponly': 'boolean(default=True)',
            'max_age': 'integer(default=None)'
        }
    )

    def __init__(
        self,
        name, dist,
        states_history,
        session_cookie, security_cookie,
        local_service, sessions_service
    ):
        super(SessionService, self).__init__(name, dist)

        self.states_history = states_history

        self.session_cookie = session_cookie
        self.security_cookie = security_cookie
        self.local = local_service
        self.sessions = sessions_service.service

    def set_cookie(self, request, response, name, data, **config):
        if name:
            response.set_cookie(name, data, path=request.script_name, **config)

    def set_session_cookie(self, request, response, session_id):
        self.set_cookie(request, response, data=str(session_id), **self.session_cookie)

    def set_secure_cookie(self, request, response, secure_token):
        self.set_cookie(request, response, data=secure_token, **self.security_cookie)

    def extract_secure_token(self, request):
        return (self.security_cookie['name'] and request.cookies.get(self.security_cookie['name'], '')).encode('ascii')

    def extract_state_ids(self, request):
        """Search the session id and the state id into the request parameters

        In:
          - ``request`` -- the web request

        Return:
          - session id
          - state id
        """
        try:
            session_id = self.session_cookie['name'] and int(request.cookies.get(self.session_cookie['name'], 0))

            return (
                session_id or int(request.params['_s']),
                int(request.params['_c']) if self.states_history else 0
            )
        except (KeyError, ValueError, TypeError):
            return None, None

    def get_state_ids(self, request):
        session_id, state_id = self.extract_state_ids(request)

        return (False, session_id, state_id) if session_id is not None else (True, None, None)

    def _handle_request(self, chain, session, **params):
        set_session(session)
        return chain.next(**params)

    def handle_request(self, chain, request, response, **params):
        new_session, session_id, state_id = self.get_state_ids(request)
        use_same_state = request.is_xhr or not self.states_history
        secure_token = self.extract_secure_token(request)
        session = Session(self.sessions, new_session, secure_token, session_id, state_id, use_same_state)

        try:
            with session.enter() as (data, callbacks):
                if self.security_cookie['name']:
                    if not session.is_new and (session.secure_token != secure_token):
                        raise exceptions.SessionSecurityError()

                self.set_session_cookie(request, response, session.session_id)
                self.set_secure_cookie(request, response, session.secure_token)

                return self._handle_request(
                    chain,
                    request=request, response=response,
                    session_id=session.session_id, state_id=session.state_id,
                    session=data, callbacks=callbacks,
                    **params
                )
        except exceptions.SessionError:
            response = request.create_redirect_response()

            if self.security_cookie['name']:
                response.delete_cookie(self.security_cookie['name'])

            if self.session_cookie['name']:
                response.delete_cookie(self.session_cookie['name'])

            raise response

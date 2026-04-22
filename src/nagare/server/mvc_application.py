# --
# Copyright (c) 2008-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.renderers import html5_base
from nagare.server.http_application import Request, RESTApp, Response  # noqa: F401

# ---------------------------------------------------------------------------


class App(RESTApp):
    """Application to handle a HTTP request."""

    CONFIG_SPEC = RESTApp.CONFIG_SPEC | {'default_content_type': 'string(default="text/html")'}
    renderer_factory = html5_base.Renderer

    def create_renderer(self, **params):
        """Create the initial renderer."""
        return self.renderer_factory(static_url=self.static_url)

    def create_dispatch_args(self, renderer, **params):
        return super().create_dispatch_args(**params) + (renderer,)

    def set_response_body(self, response, body):
        return response

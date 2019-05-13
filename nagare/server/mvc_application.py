# Encoding: utf-8

# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.renderers import html5_base
from nagare.server.http_application import Request, Response, RESTApp  # noqa: F401


def livereload(reloader, dirname, filename, url):
    if filename.endswith(('.css', '.js', '.gif', '.png', '.jpeg', '.jpg')):
        reloader.reload_asset(url + '/' + filename)

    return False

# ---------------------------------------------------------------------------


class App(RESTApp):
    """Application to handle a HTTP request"""
    CONFIG_SPEC = dict(
        RESTApp.CONFIG_SPEC,
        default_content_type='string(default="text/html")',
        static_url='string(default="/static/$app_name")',
        static='string(default="$_static_path")'
    )
    renderer_factory = html5_base.Renderer

    def __init__(self, name, dist, static_url, static, services_service, **config):
        services_service(super(App, self).__init__, name, dist, **config)

        self.static_url = static_url.rstrip('/')
        self.static_path = static.rstrip('/')

    def handle_start(self, app, services_service, statics_service, reloader_service=None):
        services_service(super(App, self).handle_start, app)

        if self.static_url:
            statics_service.register_dir(self.static_url, self.static_path)

        if reloader_service is not None:
            reloader_service.watch_dir(self.static_path, livereload, recursive=True, url=self.static_url)

    def create_renderer(self, *args, **params):
        """Create the initial renderer
        """
        return self.renderer_factory(*args)

    def create_dispatch_args(self, renderer, **params):
        return super(App, self).create_dispatch_args(**params) + (renderer,)

    def set_body(self, response, body):
        return response

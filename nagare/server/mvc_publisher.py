# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import webbrowser

from nagare.server import http_publisher


class Publisher(http_publisher.Publisher):
    CONFIG_SPEC = dict(
        http_publisher.Publisher.CONFIG_SPEC,
        open_on_start='boolean(default=True, help="open a browser tab on startup")'
    )

    def __init__(self, name, dist, open_on_start, **config):
        super(Publisher, self).__init__(name, dist, **config)
        self.open_on_start = open_on_start
        self.toto = False

    def launch_browser(self):
        is_url, endpoint = self.endpoint
        if self.open_on_start and is_url and (os.environ.get('nagare.reload', '1') == '1'):
            webbrowser.open(endpoint + '/' + self.url)

    def _serve(self, app, **params):
        self.launch_browser()

        super(Publisher, self)._serve(app, **params)

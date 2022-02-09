# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import types

from lxml import etree
from webob import Response

from nagare.services import plugin


class PresentationService(plugin.Plugin):
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        canonical_url='boolean(default=True)',
        frame_options='string(default="deny")'
    )
    LOAD_PRIORITY = 130

    def __init__(self, name, dist, canonical_url=True, frame_options='deny', **config):
        super(PresentationService, self).__init__(
            name, dist,
            canonical_url=canonical_url, frame_options=frame_options,
            **config
        )

        self.canonical_url = canonical_url
        self.frame_options = frame_options.upper()

    def merge_head(self, request, h, head, bottom, html):
        root = h.html(html)
        existing_html = [tag for tag in root if isinstance(tag, etree.ElementBase) and tag.tag == 'html']
        if len(existing_html) == 1:
            root = html
            html = existing_html[0]
        else:
            html = root

        html.tail = None

        existing_head = html.find('head')
        if existing_head is None:
            existing_head = h.head.head
            html.insert(0, existing_head)
            i = 1
        else:
            i = html.index(existing_head) + 1

        existing_body = [tag for tag in html[i:] if isinstance(tag, etree.ElementBase) and tag.tag == 'body']
        if len(existing_body) == 1:
            body = existing_body[0]
        else:
            body = h.body(existing_head.tail or '', html.text or '', html[i:])
            existing_head.tail = html.text = None
            html.append(body)

        if self.canonical_url and not head.xpath('./link[@rel="canonical"]'):
            url = request.upath_info.strip('/')
            url = request.uscript_name + ('/' if url else '') + url
            head.append(h.head.link(rel='canonical', href=url))

        existing_head.attrib.update(head.attrib)
        existing_head(head[:])

        body(bottom)

        return root

    def serialize(self, output, encoding='utf-8', doctype=None, pretty_print=False):
        if isinstance(output, etree.ElementBase):
            output.attrib.pop('xmlns', None)
            output = output.tostring(encoding=encoding, pretty_print=pretty_print, doctype=doctype)

        elif isinstance(output, type(u'')):
            output = output.encode(encoding)

        elif isinstance(output, (list, tuple, types.GeneratorType)):
            elements = list(output)
            with_doctype = any(isinstance(element, (etree.ElementBase, etree._Element)) for element in elements)
            output = ((doctype + '\n') if doctype and with_doctype else '').encode(encoding)
            output += b''.join(self.serialize(element, encoding) for element in elements)

        elif isinstance(output, etree._Element):
            output = etree.tostring(output, encoding=encoding, pretty_print=pretty_print, doctype=doctype)

        return output

    def handle_request(self, chain, app, request, response, render=None, **params):
        if not request.path_info:
            raise request.create_redirect_response()

        h = app.create_renderer(request=request, response=response, **params)

        response = chain.next(
            app=app,
            request=request, response=response,
            renderer=h,
            **params
        )

        response.content_type = h.content_type
        response.doctype = h.doctype

        body = h.root if render is None else render(h)

        if isinstance(body, Response):
            response = body
        else:
            if not request.is_xhr and ('html' in response.content_type):
                body = self.merge_head(request, h, h.head.render_top(), h.head.render_bottom(), body)
                response.headers.setdefault('X-Frame-Options', self.frame_options)

            response.body = self.serialize(
                body,
                encoding=response.charset or response.default_body_encoding,
                doctype=response.doctype if not request.is_xhr else None,
                pretty_print=True
            )

        return response

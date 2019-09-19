# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import types

from webob import exc
from lxml import etree

from nagare.services import plugin


class PresentationService(plugin.Plugin):
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        canonical_url='boolean(default=True)',
        frame_options='string(default="deny")'
    )
    LOAD_PRIORITY = 130

    def __init__(self, name, dist, canonical_url=True, frame_options='deny'):
        super(PresentationService, self).__init__(name, dist)

        self.canonical_url = canonical_url
        self.frame_options = frame_options.upper()

    def merge_head(self, request, h, head, html):
        html2 = h.html(html)
        html = html2.find('html')
        if html is None:
            html = html2

        html.tail = None

        head2 = html.find('head')
        if head2 is None:
            if html.find('body') is None:
                html.tag = 'body'
                html = h.html(html)

            head2 = h.head.head
            html.insert(0, head2)
        else:
            if html.find('body') is None:
                i = html.index(head2)
                html(h.body(head2.tail or '', html[i + 1:]))
                head2.tail = None

        if not isinstance(head, etree.ElementBase) or (head.tag != 'head'):
            head = h.head.head(head)

        if self.canonical_url and not head.xpath('./link[@rel="canonical"]'):
            url = request.upath_info.strip('/')
            url = request.uscript_name + ('/' if url else '') + url
            head.append(h.head.link(rel='canonical', href=url))

        head2.attrib.update(head.attrib)
        head2(head[:])

        return html

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
            raise exc.HTTPMovedPermanently(add_slash=True)

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

        if not request.is_xhr and ('html' in response.content_type):
            body = self.merge_head(request, h, h.head.render(), body)
            response.headers.setdefault('X-Frame-Options', self.frame_options)

        response.body = self.serialize(
            body,
            encoding=response.charset or response.default_body_encoding,
            doctype=response.doctype if not request.is_xhr else None,
            pretty_print=True
        )

        return response

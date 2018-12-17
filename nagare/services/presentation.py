# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from lxml import etree

from nagare.services import plugin


class PresentationService(plugin.Plugin):
    CONFIG_SPEC = dict(plugin.Plugin.CONFIG_SPEC, canonical_url='boolean(default=True)')
    LOAD_PRIORITY = 130

    def __init__(self, name, dist, canonical_url):
        super(PresentationService, self).__init__(name, dist)

        self.canonical_url = canonical_url

    def merge_head(self, h, head, html):
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
            url = h.request.upath_info.strip('/')
            url = h.request.uscript_name + ('/' if url else '') + url
            head.append(h.head.link(rel='canonical', href=url))

        head2.attrib.update(head.attrib)
        head2(head[:])

        return html

    def serialize(self, output, doctype='', declaration=False, pretty_print=False):
        if isinstance(output, etree.ElementBase):
            output.attrib.pop('xmlns', None)
            output = output.tostring(pretty_print=pretty_print, doctype=doctype if declaration else None)

        elif isinstance(output, type(u'')):
            output = output.encode('utf-8')

        return output

    def handle_request(self, chain, app, request, response, render=None, **params):
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
            body = self.merge_head(h, h.head.render(), body)

        response.body = self.serialize(body, response.doctype, not request.is_xhr, True)

        return response

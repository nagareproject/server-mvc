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

    def merge_head(self, h, head, body):
        if not isinstance(body, etree._Element):
            body = h.body(body)

        if body.tag != 'body':
            body = h.body(body)

        if body.tag != 'html':
            body = h.html(body)

        head1 = body.find('head')
        if head1 is None:
            body.insert(0, head)
        else:
            head1.attrib.update(head.attrib)
            head1(head[:])

        return body

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
            head = h.head.render()

            if self.canonical_url and not head.xpath('./link[@rel="canonical"]'):
                url = request.upath_info.strip('/')
                url = request.uscript_name + ('/' if url else '') + url
                head.append(h.head.link(rel='canonical', href=url))

            body = self.merge_head(h, head, body)

        response.body = self.serialize(body, response.doctype, not request.is_xhr, True)

        return response

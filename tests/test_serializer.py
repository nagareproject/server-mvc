# --
# Copyright (c) 2014-2026 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from lxml import etree

from nagare.services import presentation
from nagare.renderers import xml
from nagare.renderers import html_base as html


def test_html():
    h = html.Renderer()
    p = presentation.PresentationService(None, None, False)

    r = p.serialize(h.p('hello'))
    assert r == b'<p>hello</p>'

    r = p.serialize(h.p('été'), 'utf-8', None)
    assert r == b'<p>\xc3\xa9t\xc3\xa9</p>'

    r = p.serialize(h.p('hello'), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\n<p>hello</p>'


def test_xml():
    x = xml.Renderer()
    p = presentation.PresentationService(None, None, False)

    r = p.serialize(x.person('hello'))
    assert r == b'<person>hello</person>'

    r = p.serialize(x.person('été'), 'utf-8', None)
    assert r == b'<person>\xc3\xa9t\xc3\xa9</person>'

    r = p.serialize(x.person('hello'), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\n<person>hello</person>'


def test_comment():
    x = xml.Renderer()
    p = presentation.PresentationService(None, None, False)

    r = p.serialize(x.comment('hello'), 'utf-8')
    assert r == b'<!--hello-->'

    r = p.serialize(x.comment('été'), 'utf-8', None)
    assert r == b'<!--\xc3\xa9t\xc3\xa9-->'

    r = p.serialize(x.comment('hello'), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\n<!--hello-->'


def test_pi():
    x = xml.Renderer()
    p = presentation.PresentationService(None, None, False)

    r = p.serialize(x.processing_instruction('hello'))
    assert r == b'<?hello ?>'

    r = p.serialize(x.processing_instruction('été'), 'utf-8', None)
    assert r == b'<?\xc3\xa9t\xc3\xa9 ?>'

    r = p.serialize(x.processing_instruction('hello'), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\n<?hello ?>'


def test_etree():
    p = presentation.PresentationService(None, None, False)

    e = etree.Element('person')
    e.text = 'hello'
    r = p.serialize(e)
    assert r == b'<person>hello</person>'

    e = etree.Element('person')
    e.text = 'été'
    r = p.serialize(e, 'utf-8', None)
    assert r == b'<person>\xc3\xa9t\xc3\xa9</person>'

    e = etree.Element('person')
    e.text = 'hello'
    r = p.serialize(e, 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\n<person>hello</person>'


def test_str():
    p = presentation.PresentationService(None, None, False)

    r = p.serialize(b'hello world', 'utf-8')
    assert r == b'hello world'

    r = p.serialize('été'.encode('utf-8'), 'utf-8')
    assert r == b'\xc3\xa9t\xc3\xa9'

    r = p.serialize(b'hello world', 'utf-8', '<!DOCTYPE html>')
    assert r == b'hello world'


def test_unicode():
    p = presentation.PresentationService(None, None, False)

    r = p.serialize('hello world')
    assert r == b'hello world'

    r = p.serialize('été', 'utf-8', None)
    assert r == b'\xc3\xa9t\xc3\xa9'

    r = p.serialize('hello world', 'utf-8', '<!DOCTYPE html>')
    assert r == b'hello world'


def test_list():
    h = html.Renderer()
    x = xml.Renderer()

    p = presentation.PresentationService(None, None, False)

    r = p.serialize(['hello', 'world'])
    assert r == b'helloworld'

    r = p.serialize(['hello', 'world'], 'utf-8', '<!DOCTYPE html>')
    assert r == b'helloworld'

    r = p.serialize(('hello', 'world'))
    assert r == b'helloworld'

    r = p.serialize(('hello', 'world'), 'utf-8', '<!DOCTYPE html>')
    assert r == b'helloworld'

    def producer():
        yield 'hello'
        yield 'world'

    r = p.serialize(producer())
    assert r == b'helloworld'

    r = p.serialize(producer(), 'utf-8', '<!DOCTYPE html>')
    assert r == b'helloworld'

    r = p.serialize(['hello', 'world', h.div])
    assert r == b'helloworld<div></div>'

    r = p.serialize(['hello', 'world', h.div], 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\nhelloworld<div></div>'

    r = p.serialize(('hello', 'world', h.div))
    assert r == b'helloworld<div></div>'

    r = p.serialize(('hello', 'world', h.div), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\nhelloworld<div></div>'

    def producer():
        yield 'hello'
        yield 'world'
        yield h.div

    r = p.serialize(producer())
    assert r == b'helloworld<div></div>'

    r = p.serialize(producer(), 'utf-8', '<!DOCTYPE html>')
    assert r == b'<!DOCTYPE html>\nhelloworld<div></div>'

    e = etree.Element('person')
    e.text = 'hello'

    elements = [
        h.p('hello'),
        x.person('hello'),
        x.comment('hello'),
        x.processing_instruction('hello'),
        e,
        'hello',
        'hello',
    ]
    r = p.serialize(elements)
    assert r == b'<p>hello</p><person>hello</person><!--hello--><?hello ?><person>hello</person>hellohello'

    r = p.serialize(elements, 'utf-8', '<!DOCTYPE html>')
    assert (
        r
        == b'<!DOCTYPE html>\n<p>hello</p><person>hello</person><!--hello--><?hello ?><person>hello</person>hellohello'
    )

    elements = elements[1:] + [elements[0]]
    r = p.serialize(elements)
    assert r == b'<person>hello</person><!--hello--><?hello ?><person>hello</person>hellohello<p>hello</p>'

    r = p.serialize(elements, 'utf-8', '<!DOCTYPE html>')
    assert (
        r
        == b'<!DOCTYPE html>\n<person>hello</person><!--hello--><?hello ?><person>hello</person>hellohello<p>hello</p>'
    )

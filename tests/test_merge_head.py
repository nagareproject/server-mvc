# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import webob
from nagare.renderers import html
from nagare.services import presentation


def create_renderer(path_info, script_name):
    request = webob.Request({})
    request.path_info = path_info
    request.script_name = script_name

    return html.Renderer(request=request)


def create_presentation(canonical_url):
    return presentation.PresentationService(None, None, canonical_url)


def merge_head(presentation_service, h):
    return presentation_service.merge_head(h, h.head.root, h.root).tostring()


def test_1():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << 'hello'
    assert merge_head(p, h) == b'<html><head></head><body>hello</body></html>'

    h = create_renderer('', '')
    p = create_presentation(True)

    h << 'hello'
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href=""></head><body>hello</body></html>' \
        or merge_head(p, h) == b'<html><head><link href="" rel="canonical"></head><body>hello</body></html>'

    h = create_renderer('/a', '')
    p = create_presentation(True)

    h << 'hello'
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/a"></head><body>hello</body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/a" rel="canonical"></head><body>hello</body></html>'

    h = create_renderer('', '/b')
    p = create_presentation(True)

    h << 'hello'
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/b"></head><body>hello</body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/b" rel="canonical"></head><body>hello</body></html>'

    h = create_renderer('/a', '/b')
    p = create_presentation(True)

    h << 'hello'
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/b/a"></head><body>hello</body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/b/a" rel="canonical"></head><body>hello</body></html>'


def test_2():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << 'hello' << h.comment('c2')
    assert merge_head(p, h) == b'<html><head></head><body><!--c1-->hello<!--c2--></body></html>'


def test_3():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.p('hello')
    assert merge_head(p, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_4():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.p('hello') << h.comment('c2') << h.p('world') << h.comment('c3')
    assert merge_head(p, h) == b'<html><head></head><body><!--c1--><p>hello</p><!--c2--><p>world</p><!--c3--></body></html>'


def test_5():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.body('hello')
    assert merge_head(p, h) == b'<html><head></head><body>hello</body></html>'


def test_6():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.body('hello') << h.comment('c2')
    assert merge_head(p, h) == b'<html><head></head><!--c1--><body>hello</body><!--c2--></html>'


def test_7():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.body(h.p('hello'))
    assert merge_head(p, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_8():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.body(h.p('hello')) << h.comment('c2')
    assert merge_head(p, h) == b'<html><head></head><!--c1--><body><p>hello</p></body><!--c2--></html>'


def test_9():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.head.head
    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_10():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.head.head << h.comment('c2')
    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><!--c2--></body></html>'


def test_11():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.head.head << 'hello'
    assert merge_head(p, h) == b'<html><head></head><body>hello</body></html>'


def test_12():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2')
    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><p>hello</p><!--c2--></body></html>'


def test_13():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.head.head << h.comment('c2') << h.p('hello') << h.comment('c3')
    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><!--c2--><p>hello</p><!--c3--></body></html>'


def test_14():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.head.head << h.body
    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_15():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.head.head << h.comment('c2') << h.body << h.comment('c3')
    assert merge_head(p, h) == b'<html><!--c1--><head></head><!--c2--><body></body><!--c3--></html>'


def test_16():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.head.head << 'hello' << h.body << 'world'
    assert merge_head(p, h) == b'<html><head></head>hello<body></body>world</html>'


def test_17():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2') << h.body('world') << h.comment('c3')
    assert merge_head(p, h) == b'<html><!--c1--><head></head><p>hello</p><!--c2--><body>world</body><!--c3--></html>'


def test_18():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.html << 'hello'

    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_19():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.comment('c1') << h.html << 'hello' << h.comment('c2')
    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_20():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.p('hello')

    assert merge_head(p, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_21():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.p('hello') << h.comment('c2') << h.p('world') << h.comment('c3')

    assert merge_head(p, h) == b'<html><head></head><body><!--c1--><p>hello</p><!--c2--><p>world</p><!--c3--></body></html>'


def test_22():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.body('hello')

    assert merge_head(p, h) == b'<html><head></head><body>hello</body></html>'


def test_23():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.body('hello') << h.comment('c2')

    assert merge_head(p, h) == b'<html><head></head><!--c1--><body>hello</body><!--c2--></html>'


def test_24():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.body(h.p('hello'))

    assert merge_head(p, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_25():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.body(h.p('hello')) << h.comment('c2')

    assert merge_head(p, h) == b'<html><head></head><!--c1--><body><p>hello</p></body><!--c2--></html>'


def test_26():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.head.head

    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_27():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2')

    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><!--c2--></body></html>'


def test_28():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.head.head << 'hello'

    assert merge_head(p, h) == b'<html><head></head><body>hello</body></html>'


def test_29():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2')

    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><p>hello</p><!--c2--></body></html>'


def test_30():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2') << h.p('hello') << h.comment('c3')

    assert merge_head(p, h) == b'<html><!--c1--><head></head><body><!--c2--><p>hello</p><!--c3--></body></html>'


def test_31():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.head.head << h.body

    assert merge_head(p, h) == b'<html><head></head><body></body></html>'


def test_32():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2') << h.body << h.comment('c3')

    assert merge_head(p, h) == b'<html><!--c1--><head></head><!--c2--><body></body><!--c3--></html>'


def test_33():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.head.head << 'hello' << h.body << 'world'

    assert merge_head(p, h) == b'<html><head></head>hello<body></body>world</html>'


def test_34():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    with h.html:
        h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2') << h.body('world') << h.comment('c3')

    assert merge_head(p, h) == b'<html><!--c1--><head></head><p>hello</p><!--c2--><body>world</body><!--c3--></html>'


def test_35():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h.head << h.head.title('hello')
    h << h.p('world')

    assert merge_head(p, h) == b'<html><head><title>hello</title></head><body><p>world</p></body></html>'


def test_36():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h.head << h.head.title('hello')
    h << h.head.head(h.head.title('world')) << h.p('foo')

    assert merge_head(p, h) == b'<html><head><title>world</title><title>hello</title></head><body><p>foo</p></body></html>'


def test_37():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h.head << h.head.head(id='header_id')
    h << h.head.head(class_='header_class') << h.p('foo')

    assert merge_head(p, h) == b'<html><head class="header_class" id="header_id"></head><body><p>foo</p></body></html>'


def test_38():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.processing_instruction('hello') << h.p('foo') << h.processing_instruction('world')

    assert merge_head(p, h) == b'<html><head></head><body><?hello ><p>foo</p><?world ></body></html>'


def test_39():
    h = create_renderer('/a', '/b')
    p = create_presentation(False)

    h << h.processing_instruction('hello') << h.html(h.p('foo'))

    assert merge_head(p, h) == b'<html><head></head><body><p>foo</p></body></html>'


def test_canonical():
    h = create_renderer('', '')
    p = create_presentation(True)

    assert merge_head(p, h) == b'<html><head><link rel="canonical" href=""></head><body></body></html>' \
        or merge_head(p, h) == b'<html><head><link href="" rel="canonical"></head><body></body></html>'

    h = create_renderer('', '')
    p = create_presentation(True)

    h.head << h.head.link(rel='canonical', href='/bar')
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/bar"></head><body></body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/bar" rel="canonical"></head><body></body></html>'

    h = create_renderer('/foo', '')
    p = create_presentation(True)

    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/foo"></head><body></body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/foo" rel="canonical"></head><body></body></html>'

    h = create_renderer('/foo', '')
    p = create_presentation(True)

    h.head << h.head.link(rel='canonical', href='/bar')
    assert merge_head(p, h) == b'<html><head><link rel="canonical" href="/bar"></head><body></body></html>' \
        or merge_head(p, h) == b'<html><head><link href="/bar" rel="canonical"></head><body></body></html>'

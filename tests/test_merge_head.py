# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from lxml import etree

import webob
from nagare.renderers import html_base as html

from nagare.services import presentation


def create_request(path_info, script_name):
    return webob.Request({'PATH_INFO': path_info, 'SCRIPT_NAME': script_name})


def create_presentation(canonical_url):
    return presentation.PresentationService(None, None, canonical_url)


def merge_head(presentation_service, request, h):
    output = presentation_service.merge_head(request, h, h.head.render_top(), h.head.render_bottom(), h.root)
    if isinstance(output, list):
        return [etree.tostring(tag) if etree.iselement(tag) else str(tag).encode('utf-8') for tag in output]
    else:
        return output.tostring()


def test_1():
    p = create_presentation(False)
    r = create_request('/a', '/b')
    h = html.Renderer()

    h << 'hello'
    assert merge_head(p, r, h) == b'<html><head></head><body>hello</body></html>'

    r = create_request('', '')
    p = create_presentation(True)
    h = html.Renderer()

    h << 'hello'
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href=""></head><body>hello</body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="" rel="canonical"></head><body>hello</body></html>'

    r = create_request('/a', '')
    p = create_presentation(True)
    h = html.Renderer()

    h << 'hello'
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/a"></head><body>hello</body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/a" rel="canonical"></head><body>hello</body></html>'

    r = create_request('', '/b')
    p = create_presentation(True)
    h = html.Renderer()

    h << 'hello'
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/b"></head><body>hello</body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/b" rel="canonical"></head><body>hello</body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(True)
    h = html.Renderer()

    h << 'hello'
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/b/a"></head><body>hello</body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/b/a" rel="canonical"></head><body>hello</body></html>'


def test_2():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << 'hello' << h.comment('c2')
    assert merge_head(p, r, h) == b'<html><head></head><body><!--c1-->hello<!--c2--></body></html>'


def test_3():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.p('hello')
    assert merge_head(p, r, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_4():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.p('hello') << h.comment('c2') << h.p('world') << h.comment('c3')
    assert merge_head(p, r, h) == b'<html><head></head><body><!--c1--><p>hello</p><!--c2--><p>world</p><!--c3--></body></html>'


def test_5():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.body('hello')
    assert merge_head(p, r, h) == b'<html><head></head><body>hello</body></html>'


def test_6():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.body('hello') << h.comment('c2')
    assert merge_head(p, r, h) == b'<html><head></head><!--c1--><body>hello</body><!--c2--></html>'


def test_7():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.body(h.p('hello'))
    assert merge_head(p, r, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_8():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.body(h.p('hello')) << h.comment('c2')
    assert merge_head(p, r, h) == b'<html><head></head><!--c1--><body><p>hello</p></body><!--c2--></html>'


def test_9():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.head.head
    assert merge_head(p, r, h) == b'<html><head></head><body></body></html>'


def test_10():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.head.head << h.comment('c2')
    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><!--c2--></body></html>'


def test_11():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.head.head << 'hello'
    assert merge_head(p, r, h) == b'<html><head></head><body>hello</body></html>'


def test_12():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2')
    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><p>hello</p><!--c2--></body></html>'


def test_13():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.head.head << h.comment('c2') << h.p('hello') << h.comment('c3')
    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><!--c2--><p>hello</p><!--c3--></body></html>'


def test_14():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.head.head << h.body
    assert merge_head(p, r, h) == b'<html><head></head><body></body></html>'


def test_15():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.head.head << h.comment('c2') << h.body << h.comment('c3')
    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><!--c2--><body></body><!--c3--></html>'


def test_16():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.head.head << 'hello' << h.body << 'world'
    assert merge_head(p, r, h) == b'<html><head></head>hello<body></body>world</html>'


def test_17():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2') << h.body('world') << h.comment('c3')
    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><p>hello</p><!--c2--><body>world</body><!--c3--></html>'


def test_18():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.html(id='foo') << 'hello'

    assert merge_head(p, r, h) == [b'<html id="foo"><head/><body/></html>', b'hello']


def test_19():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.comment('c1') << h.html << 'hello' << h.comment('c2')
    assert merge_head(p, r, h) == [b'<!--c1-->', b'<html><head/><body/></html>', b'hello', b'<!--c2-->']


def test_20():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.p('hello')

    assert merge_head(p, r, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_21():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.p('hello') << h.comment('c2') << h.p('world') << h.comment('c3')

    assert merge_head(p, r, h) == b'<html><head></head><body><!--c1--><p>hello</p><!--c2--><p>world</p><!--c3--></body></html>'


def test_22():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.body('hello')

    assert merge_head(p, r, h) == b'<html><head></head><body>hello</body></html>'


def test_23():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.body('hello') << h.comment('c2')

    assert merge_head(p, r, h) == b'<html><head></head><!--c1--><body>hello</body><!--c2--></html>'


def test_24():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.body(h.p('hello'))

    assert merge_head(p, r, h) == b'<html><head></head><body><p>hello</p></body></html>'


def test_25():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.body(h.p('hello')) << h.comment('c2')

    assert merge_head(p, r, h) == b'<html><head></head><!--c1--><body><p>hello</p></body><!--c2--></html>'


def test_26():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.head.head

    assert merge_head(p, r, h) == b'<html><head></head><body></body></html>'


def test_27():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2')

    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><!--c2--></body></html>'


def test_28():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.head.head << 'hello'

    assert merge_head(p, r, h) == b'<html><head></head><body>hello</body></html>'


def test_29():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2')

    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><p>hello</p><!--c2--></body></html>'


def test_30():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2') << h.p('hello') << h.comment('c3')

    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><body><!--c2--><p>hello</p><!--c3--></body></html>'


def test_31():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.head.head << h.body

    assert merge_head(p, r, h) == b'<html><head></head><body></body></html>'


def test_32():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.head.head << h.comment('c2') << h.body << h.comment('c3')

    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><!--c2--><body></body><!--c3--></html>'


def test_33():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.head.head << 'hello' << h.body << 'world'

    assert merge_head(p, r, h) == b'<html><head></head>hello<body></body>world</html>'


def test_34():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    with h.html:
        h << h.comment('c1') << h.head.head << h.p('hello') << h.comment('c2') << h.body('world') << h.comment('c3')

    assert merge_head(p, r, h) == b'<html><!--c1--><head></head><p>hello</p><!--c2--><body>world</body><!--c3--></html>'


def test_35():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h.head << h.head.title('hello')
    h << h.p('world')

    assert merge_head(p, r, h) == b'<html><head><title>hello</title></head><body><p>world</p></body></html>'


def test_36():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h.head << h.head.title('hello')
    h << h.head.head(h.head.title('world')) << h.p('foo')

    assert merge_head(p, r, h) == b'<html><head><title>world</title><title>hello</title></head><body><p>foo</p></body></html>'


def test_37():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h.head << h.head.head(id='header_id')
    h << h.head.head(class_='header_class') << h.p('foo')

    assert merge_head(p, r, h) == b'<html><head class="header_class" id="header_id"></head><body><p>foo</p></body></html>'


def test_38():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.processing_instruction('hello') << h.p('foo') << h.processing_instruction('world')

    assert merge_head(p, r, h) == b'<html><head></head><body><?hello ><p>foo</p><?world ></body></html>'


def test_39():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.processing_instruction('hello') << h.html(h.p('foo'))
    assert merge_head(p, r, h) == [b'<?hello ?>', b'<html><head/><body><p>foo</p></body></html>']


def test_40():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.html(h.p('foo'), id='html')
    assert merge_head(p, r, h) == b'<html id="html"><head></head><body><p>foo</p></body></html>'


def test_41():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.html(h.head.head(h.head.title, id='head'), h.p('foo'), id='html')
    assert merge_head(p, r, h) == b'<html id="html"><head id="head"><title></title></head><body><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << h.html(h.head.head(h.head.title, id='head'), h.p('foo'), id='html')
    result = merge_head(p, r, h)
    assert result == b'<html id="html"><head id="head"><title></title><script type="text/javascript" src="/foo.js"></script></head><body><p>foo</p></body></html>' \
        or result == b'<html id="html"><head id="head"><title></title><script src="/foo.js" type="text/javascript"></script></head><body><p>foo</p></body></html>'


def test_42():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.html(h.body(h.p('foo'), id="body"), id='html')
    assert merge_head(p, r, h) == b'<html id="html"><head></head><body id="body"><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << h.html(h.body(h.p('foo'), id="body"), id='html')
    result = merge_head(p, r, h)
    assert result == b'<html id="html"><head><script type="text/javascript" src="/foo.js"></script></head><body id="body"><p>foo</p></body></html>' \
        or result == b'<html id="html"><head><script src="/foo.js" type="text/javascript"></script></head><body id="body"><p>foo</p></body></html>'


def test_43():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.html(h.head.head(h.head.title, id='head'), h.body(h.p('foo'), id="body"), id='html')
    assert merge_head(p, r, h) == b'<html id="html"><head id="head"><title></title></head><body id="body"><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << h.html(h.head.head(h.head.title, id='head'), h.body(h.p('foo'), id="body"), id='html')
    result = merge_head(p, r, h)
    assert result == b'<html id="html"><head id="head"><title></title><script type="text/javascript" src="/foo.js"></script></head><body id="body"><p>foo</p></body></html>' \
        or result == b'<html id="html"><head id="head"><title></title><script src="/foo.js" type="text/javascript"></script></head><body id="body"><p>foo</p></body></html>'


def test_44():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << [h.head.head(h.head.title, id='head'), h.p('foo')]
    assert merge_head(p, r, h) == b'<html><head id="head"><title></title></head><body><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << [h.head.head(h.head.title, id='head'), h.p('foo')]
    result = merge_head(p, r, h)
    assert result == b'<html><head id="head"><title></title><script type="text/javascript" src="/foo.js"></script></head><body><p>foo</p></body></html>' \
        or result == b'<html><head id="head"><title></title><script src="/foo.js" type="text/javascript"></script></head><body><p>foo</p></body></html>'


def test_45():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << [h.head.head(h.head.title, id='head'), h.body(h.p('foo'), id="body")]
    assert merge_head(p, r, h) == b'<html><head id="head"><title></title></head><body id="body"><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << [h.head.head(h.head.title, id='head'), h.body(h.p('foo'), id="body")]
    result = merge_head(p, r, h)
    assert result == b'<html><head id="head"><title></title><script type="text/javascript" src="/foo.js"></script></head><body id="body"><p>foo</p></body></html>' \
        or result == b'<html><head id="head"><title></title><script src="/foo.js" type="text/javascript"></script></head><body id="body"><p>foo</p></body></html>'


def test_46():
    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()

    h << h.body(h.p('foo'), id="body")
    assert merge_head(p, r, h) == b'<html><head></head><body id="body"><p>foo</p></body></html>'

    r = create_request('/a', '/b')
    p = create_presentation(False)
    h = html.Renderer()
    h.head.javascript_url('/foo.js')

    h << h.body(h.p('foo'), id="body")
    result = merge_head(p, r, h)
    assert result == b'<html><head><script type="text/javascript" src="/foo.js"></script></head><body id="body"><p>foo</p></body></html>' \
        or result == b'<html><head><script src="/foo.js" type="text/javascript"></script></head><body id="body"><p>foo</p></body></html>'


def test_canonical():
    r = create_request('', '')
    p = create_presentation(True)
    h = html.Renderer()

    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href=""></head><body></body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="" rel="canonical"></head><body></body></html>'

    r = create_request('', '')
    p = create_presentation(True)
    h = html.Renderer()

    h.head << h.head.link(rel='canonical', href='/bar')
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/bar"></head><body></body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/bar" rel="canonical"></head><body></body></html>'

    r = create_request('/foo', '')
    p = create_presentation(True)
    h = html.Renderer()

    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/foo"></head><body></body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/foo" rel="canonical"></head><body></body></html>'

    r = create_request('/foo', '')
    p = create_presentation(True)
    h = html.Renderer()

    h.head << h.head.link(rel='canonical', href='/bar')
    assert merge_head(p, r, h) == b'<html><head><link rel="canonical" href="/bar"></head><body></body></html>' \
        or merge_head(p, r, h) == b'<html><head><link href="/bar" rel="canonical"></head><body></body></html>'

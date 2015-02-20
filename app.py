#!/usr/bin/env python
import os
import asyncio
from aiohttp import web
import tenjin
from tenjin.helpers import *
from shpaml import convert_text as convert_shpaml
from functools import wraps

BASE=os.environ['VIRTUAL_ENV']

def ShpamlPreprocessor(inp,**kws):
    return convert_shpaml(inp)

engine=tenjin.Engine(
    path=[os.path.join(BASE,'views')],
    pp=[ShpamlPreprocessor]
)

def with_template(template_name,engine=engine,content_type='text/html'):
    def dec(f):
        @wraps(f)
        @asyncio.coroutine
        def inner(*args,**kws):
            return web.Response(text=engine.render(template_name,context=f(*args,**kws)),content_type=content_type)
        return inner
    return dec

def to_json(content_type='text/json'):
    def dec(f):
        @wraps(f)
        @asyncio.coroutine
        def inner(*args,**kws):
            return web.Response(text=ujson.dumps(f(*args,**kws)),content_type=content_type)
        return inner
    return dec


@with_template('meh.spml')
def hello(request):
    return {'foo':'bar'}

import ujson
@to_json()
def json_test(request):
    return [
        1,
        2,
        {
            3: 'a',
            4: 'b',
        }
    ]

app = web.Application()
app.router.add_route('GET', '/', hello)
app.router.add_route('GET', '/json', json_test)
app.router.add_static('/js',os.path.join(BASE,'static','js'))
app.router.add_static('/img',os.path.join(BASE,'static','img'))
app.router.add_static('/css',os.path.join(BASE,'static','css'))
app.router.add_static('/html',os.path.join(BASE,'static','html'))

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    f = loop.create_server(app.make_handler(), '0.0.0.0', 8080)
    srv = loop.run_until_complete(f)
    print('serving on', srv.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

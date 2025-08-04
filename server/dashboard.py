
import asyncio
import sys

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task
from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web import server, resource
from autobahn.twisted.resource import WebSocketResource

from jinja2 import Environment, FileSystemLoader, select_autoescape

from rx import RxFactory
from tx import TxFactory
from data import datastore

from twisted.python import log

CONF = {
        'DASHBOARD': {},
        'Port': 8891,
}


class Search(resource.Resource):

    def render_GET(self, request):
        data = datastore.get_phonebook()
        sorted_data = sorted(data, key=lambda x: x["extension"])
        filter_data = []
        q = request.args.get(b'q', [b''])[0].decode().upper()
        for x in sorted_data:
            s = x.get('displayname', '').upper()
            c = x.get('callsign', '').upper()
            print(f'q="{q}" s="{s}" c="{c}"')
            if q in s or q in c:
                filter_data.append(x)

        request.setHeader(b'Content-Type', b'application/xml')
        tmpl_res = env.get_template("results.xml")
        return tmpl_res.render(conf=CONF["DASHBOARD"], data=filter_data).encode('utf-8')




class Page(resource.Resource):

    isLeaf = True
    _template = None
    _part = None

    def __init__(self, *args, **kwargs):
        self._template = kwargs.pop('template', None)
        self._part = kwargs.pop('part', None)
        self._headers = kwargs.pop('headers', [])
        super().__init__(*args, **kwargs)

    def render_GET(self, request):
        if self._headers is not None:
            for i in self._headers:
                request.setHeader(i[0], i[1])
        data = datastore.get_phonebook()
        sorted_data = sorted(data, key=lambda x: x["extension"])
        return self._template.render(conf=CONF["DASHBOARD"], data=sorted_data, page=self._part).encode('utf-8')



if __name__ == "__main__":

    print('MMD - Multimode Dashboard')
    print('(C) Copyright 2005, Jared Quinn VK2WAY <jared@jaredquinn.info>')

    print('dashboard.py starting up')
    print('')

    log.startLogging(sys.stdout)
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"])
    )

    tmpl_home = env.get_template("index.html")
    tmpl_dirapp = env.get_template("directory.xml")

    txf = TxFactory(data=datastore)
    txf.startFactory()
    tx = WebSocketResource(txf)

    rxf = RxFactory(sender=txf, data=datastore, config=CONF)
    rxf.startFactory()
    rx = WebSocketResource(rxf)

    client_pinger = task.LoopingCall(txf.pingall)
    client_pinger.start(10)

    root = resource.Resource()
    root.putChild(b"", Page(template=tmpl_home, part='home'))
    root.putChild(b"rx", rx)
    root.putChild(b"ws", tx)
    root.putChild(b"directory", Page(template=tmpl_dirapp, headers=[(b'Content-Type', b'application/xml')]))
    root.putChild(b"search", Search()),
    root.putChild(b"static", File("static"))

    site = Site(root)
    log.msg('Listening for HTTP/WS connections on %s' % CONF.get('Port', 8891))

    reactor.listenTCP(CONF.get('Port', 8891), site)
    reactor.run()


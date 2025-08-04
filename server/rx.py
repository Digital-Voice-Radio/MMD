
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.python import log

import json


class RxProtocol(WebSocketServerProtocol):

    system = None

    def onConnect(self, request):
        log.msg(f"Sender connecting: {request.peer}")

    def onOpen(self):
        log.msg("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
        #self.factory.unregister(self)
        log.msg(f"WebSocket connection closed: {reason}")

    def onMessage(self, data, isbin):
        o = json.loads(data)
        if o.get('_data') == 'PING':
            self.sendMessage(json.dumps({'_data': 'PONG'}).encode('utf-8'))

        elif o.get('_data') == 'SYSTEM':
            self.system = o
            print(o)

        else:
            o['exchange'] = self.system.get('_service')
            changed = self.factory.data.update(o, config=self.factory.config)
            print(f'CHANGED {o}: {changed}')
            if changed is not None:
                self.factory.relay(changed)


class RxFactory(WebSocketServerFactory):
    protocol = RxProtocol
    data = None
    sender = None
    config = None

    def __init__(self, sender, data, config):
        self.sender = sender
        self.data = data
        self.config = config
        WebSocketServerFactory.__init__(self)

    def relay(self, msg):
        self.sender.broadcast(json.dumps(msg))


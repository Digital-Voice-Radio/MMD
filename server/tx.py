from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.python import log

import json


class TxProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        log.msg(f"Sender connecting: {request.peer}")

    def onOpen(self):
        log.msg("WebSocket connection open.")
        self.factory.register(self)

    def onClose(self, clean, code, reason):
        log.msg("WebSocket connection close.")
        self.factory.register(self)

    def onConnectionLost(self):
        self.factory.unregister(self)

    def onMessage(self, data, isbin):
        log.msg('The web client is talking, please tell it not to.')


class TxFactory(WebSocketServerFactory):

    protocol = TxProtocol
    data = None

    def __init__(self, data):
        super().__init__()
        self.clients = []
        self.data = data

    def pingall(self):
        self.broadcast(json.dumps({'action': 'PING'}))

    def broadcast(self, msg):
        log.msg(f"broadcasting message to: {self.clients}")
        log.msg(msg)
        for client in self.clients:
            try:
                client.sendMessage(msg.encode("utf8"))
            except:
                print("Removing client due to send error.")
                self.unregister(client)


    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)
            log.msg(f"registered client {client.peer}")
        client.sendMessage(json.dumps(self.data.get_phonebook()).encode('utf-8'))


    def unregister(self, client):
        log.msg(f"unregistered client {client.peer}")
        if client in self.clients:
            self.clients.remove(client)


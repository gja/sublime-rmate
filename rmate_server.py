import asyncore
import asynchat
import socket
import threading


class RMateServer(asyncore.dispatcher):
    def __init__(self, sublime_plugin, connection_details = ('localhost', 52698)):
        asyncore.dispatcher.__init__(self)
        self.sublime_plugin = sublime_plugin
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(connection_details)
        self.listen(5)

    def run(self):
        server_thread = threading.Thread(target=asyncore.loop)
        server_thread.daemon = True
        server_thread.start()

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            RMateHandler(sock)


class RMateHandler(asynchat.async_chat):
    def __init__(self, sock):
        self.received_data = ""
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator('\n')

    def collect_incoming_data(self, data):
        self.received_data += data

    def found_terminator(self):
        print self.received_data

server = RMateServer("foobar")
server.run()
string = input()
server.shutdown()

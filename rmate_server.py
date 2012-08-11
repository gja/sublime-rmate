import SocketServer
import socket
import threading


class RMateServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, sublime_plugin, connection_details = ('localhost', 52698)):
        SocketServer.TCPServer.__init__(self, connection_details, RMateHandler)
        self.sublime_plugin = sublime_plugin

    def run(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()


class RMateHandler(SocketServer.StreamRequestHandler):
    def say_hello(self):
        self.wfile.write(socket.gethostname() + "\n")

    def handle(self):
        self.say_hello()

        cmd = self.rfile.readline().rstrip()
        print cmd


server = RMateServer("foobar")
server.run()
string = input()
server.shutdown()

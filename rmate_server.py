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
        # asyncore.loop()
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


class RMateHandler(asyncore.dispatcher_with_send):
    def init(self, sock):
        asyncore.file_wrapper.__init__(self, sock)
        self.current_line = ""

    def handle_connect(self):
        print "foobar"
        # self.send(socket.gethostname() + "\n")

    def handle_accept(self):
        print "blah"

    def handle_read(self):
        data = self.recv(10)
        if '\n' in data:
            print "line"
        else:
            print "no line"

    def handle(self):
        self.say_hello()

        cmd = self.rfile.readline().rstrip()
        print cmd


server = RMateServer("foobar")
server.run()
string = input()
server.shutdown()

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
            handler = RMateHandler(sock)
            handler.say_hello()


class WaitingForCommand:
    def __init__(self, handler):
        self.handler = handler
        self.handler.set_terminator('\n')

    def data_received(self, data):
        return WaitingForHeaders(data, self.handler)


class WaitingForHeaders:
    def __init__(self, cmd, handler):
        self.cmd = cmd
        self.handler = handler
        self.handler.set_terminator('\n')
        self.headers = {}

    def data_received(self, data):
        key, value = data.split(': ', 1)
        self.headers[key] = value
        if key != "data":
            return self
        elif int(value) == 0:
            return WaitingForDot(self.cmd, self.headers, "", self.handler)
        else:
            return WaitingForData(self.cmd, self.headers, self.handler)


class WaitingForData:
    def __init__(self, cmd, headers, handler):
        self.cmd = cmd
        self.headers = headers
        self.handler = handler
        self.handler.set_terminator(int(headers["data"]))

    def data_received(self, data):
        return WaitingForDot(self.cmd, self.headers, data, self.handler)


class WaitingForDot:
    def __init__(self, cmd, headers, data, handler):
        self.cmd = cmd
        self.headers = headers
        self.data = data
        self.handler = handler
        self.handler.set_terminator("\n")

    def data_received(self, data):
        print "the data is " + self.data  # and open sublime
        return WaitingForCommand(self.handler)


class RMateHandler(asynchat.async_chat):
    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock)
        self.received_data = ""
        self.state = WaitingForCommand(self)

    def say_hello(self):
        self.push(socket.gethostname() + "\n")

    def collect_incoming_data(self, data):
        self.received_data += data

    def found_terminator(self):
        if self.received_data == "":
            return
        self.state = self.state.data_received(self.received_data)
        self.received_data = ""

server = RMateServer("foobar")
server.run()
string = input()
server.shutdown()

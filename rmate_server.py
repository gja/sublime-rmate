import asyncore
import asynchat
import socket
import threading


# Ugly hack to communicate with the asyncore thread
class RunOnThread(asyncore.dispatcher):
    def __init__(self, block, map):
        self.block = block
        asyncore.dispatcher.__init__(self, map=map)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('localhost', 52698))

    def handle_connect(self):
        self.block()
        self.close()


class RMateServer(asyncore.dispatcher):
    def __init__(self, sublime_plugin, connection_details = ('localhost', 52698)):
        self.run_map = {}
        asyncore.dispatcher.__init__(self, map=self.run_map)
        self.sublime_plugin = sublime_plugin
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(connection_details)
        self.listen(5)

    def run(self):
        server_thread = threading.Thread(target=lambda: asyncore.loop(map=self.run_map))
        server_thread.daemon = True
        server_thread.start()

    def running(self):
        return True

    def close_all(self):
        for channel in self.run_map.values():
            channel.close()

    def run_on_thread(self, block):
        RunOnThread(lambda: block(self), self.run_map)

    # These two methods are really implementation bound
    def get_handler_by_id(self, handler_id):
        return self.run_map[handler_id]

    def get_handler_id(self, handler):
        return handler.handler_id()

    def close_file(self, handler_id, token):
        handler = self.get_handler_by_id(handler_id)
        if handler == None:
            return
        handler.close_file(token)

    def update_file(self, handler_id, token, contents):
        handler = self.get_handler_by_id(handler_id)
        if handler == None:
            return
        handler.write_file(token, contents)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            handler = RMateHandler(sock, self.sublime_plugin, self.run_map)
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
        self.handler.open_file(self.headers["token"], self.data)
        return WaitingForCommand(self.handler)


class RMateHandler(asynchat.async_chat):
    def __init__(self, sock, sublime_plugin, run_map):
        asynchat.async_chat.__init__(self, sock, map=run_map)
        self.received_data = ""
        self.state = WaitingForCommand(self)
        self.sublime_plugin = sublime_plugin
        self.open_files = []

    def say_hello(self):
        self.push(socket.gethostname() + "\n")

    def open_file(self, token, contents):
        self.open_files.append(token)
        self.sublime_plugin.open_file(token, contents, self.handler_id())

    def collect_incoming_data(self, data):
        self.received_data += data

    def found_terminator(self):
        if self.received_data == "":
            return
        self.state = self.state.data_received(self.received_data)
        self.received_data = ""

    def write_file(self, token, file_contents):
        command = """save
token: {token}
data: {length}
{file_contents}
""".format(token=token, length=len(file_contents), file_contents=file_contents)
        self.push(command)

    def close_file(self, token):
        command = """close
token: {token}

""".format(token=token)
        self.push(command)
        self.open_files.remove(token)
        if not self.open_files:
            self.close()

    def handler_id(self):
        return self.socket.fileno()

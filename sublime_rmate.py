import sublime
import sublime_plugin
from rmate_server import *


class NullServer:
    def running(self):
        False

    def run_on_thread(self, block):
        pass


class SublimeRmateAdapter:
    singleton_instance = None

    def __init__(self):
        self.server = NullServer()

    @classmethod
    def instance(cls):
        if not cls.singleton_instance:
            cls.singleton_instance = SublimeRmateAdapter()
        return cls.singleton_instance

    def start_server(self):
        if self.server.running():
            print "rmate server already running"
            return
        print "rmate server staring"
        self.server = RMateServer(self)
        self.server.run()

    def stop_server(self):
        print "stopping rmate server"
        self.server.run_on_thread(lambda server: server.close_all())
        self.server = NullServer()

    def close_handler(self, handler_id):
        self.server.run_on_thread(lambda server: server.close_handler(handler_id))

    def run_in_sublime(self, proc):
        sublime.set_timeout(proc, 1)

    def open_file(self, token, contents, handler_id):
        self.run_in_sublime(lambda: self.open_file_threaded(token, contents, handler_id))

    def open_file_threaded(self, token, contents, handler_id):
        window = sublime.active_window()
        view = window.new_file()
        view.settings().set("rmate_handler_id", handler_id)
        view.set_name(token)
        view.run_command("insert", {"characters": contents})


class StartRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().start_server()


class StopRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().stop_server()


class SublimeRmateEventListener(sublime_plugin.EventListener):
    def on_close(self, view):
        handler_id = view.settings().get("rmate_handler_id")
        if handler_id == None:
            return
        SublimeRmateAdapter.instance().close_handler(handler_id)

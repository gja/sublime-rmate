import sublime
import sublime_plugin
from rmate_server import *


class SublimeRmateAdapter:
    singleton_instance = None

    def __init__(self):
        self.server = None

    @classmethod
    def instance(cls):
        if not cls.singleton_instance:
            cls.singleton_instance = SublimeRmateAdapter()
        return cls.singleton_instance

    def is_server_running(self):
        if self.server:
            return True
        else:
            return False

    def start_server(self):
        if self.is_server_running():
            return
        print "rmate server staring"
        self.server = RMateServer(self)
        self.server.run()

    def stop_server(self):
        if not self.is_server_running():
            return
        print "stopping rmate server"
        self.server.close()
        self.server = None

    def run_in_sublime(self, proc):
        sublime.set_timeout(proc, 1)

    def open_file(self, token, contents):
        self.run_in_sublime(lambda: self.open_file_threaded(token, contents))

    def open_file_threaded(self, token, contents):
        window = sublime.active_window()
        view = window.new_file()
        view.set_name(token)
        view.run_command("insert", {"characters": contents})


class StartRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().start_server()


class StopRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().stop_server()

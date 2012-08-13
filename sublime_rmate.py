import sublime
import sublime_plugin
import tempfile
from rmate_server import *
import re


class NullServer:
    def running(self):
        False

    def run_on_thread(self, block):
        pass


class SublimeRmateView:
    def __init__(self, sublime_view):
        self.sublime_view = sublime_view

    @classmethod
    def create_file_on_filesystem(cls, token, contents):
        new_file = tempfile.NamedTemporaryFile(delete=False, suffix=re.sub("[^a-zA-Z0-9._-]", "", token))
        new_file.write(contents)
        filename = new_file.name
        new_file.close()
        return filename

    @classmethod
    def new_file(cls, token, contents, handler_id):
        filename = cls.create_file_on_filesystem(token, contents)
        window = sublime.active_window()
        view = SublimeRmateView(window.open_file(filename))
        view.set_rmate_properties(handler_id, token)
        return view

    def set_rmate_properties(self, handler_id, token):
        self.sublime_view.settings().set("rmate_handler_id", handler_id)
        self.sublime_view.settings().set("rmate_handler_token", token)

    def handler_id(self):
        return self.sublime_view.settings().get("rmate_handler_id")

    def token(self):
        return self.sublime_view.settings().get("rmate_handler_token")

    def not_rmate_file(self):
        return not self.sublime_view.settings().has("rmate_handler_id")

    def contents(self):
        return self.sublime_view.substr(sublime.Region(0, self.sublime_view.size()))


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

    def close_file(self, handler_id, token):
        self.server.run_on_thread(lambda server: server.close_file(handler_id, token))

    def update_file(self, handler_id, token, contents):
        self.server.run_on_thread(lambda server: server.update_file(handler_id, token, contents))

    def run_in_sublime(self, proc):
        sublime.set_timeout(proc, 1)

    def open_file(self, token, contents, handler_id):
        self.run_in_sublime(lambda: SublimeRmateView.new_file(token, contents, handler_id))


class StartRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().start_server()


class StopRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        SublimeRmateAdapter.instance().stop_server()


class SublimeRmateEventListener(sublime_plugin.EventListener):
    def on_close(self, view):
        rmate_view = SublimeRmateView(view)
        if rmate_view.not_rmate_file():
            return
        SublimeRmateAdapter.instance().close_file(rmate_view.handler_id(), rmate_view.token())

    def on_post_save(self, view):
        rmate_view = SublimeRmateView(view)
        if rmate_view.not_rmate_file():
            return
        print "saving remote file"
        SublimeRmateAdapter.instance().update_file(rmate_view.handler_id(), rmate_view.token(), rmate_view.contents())

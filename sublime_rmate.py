import sublime
import sublime_plugin
from rmate_server import *


class StartRmateCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        self.server = RMateServer(self)
        self.server.run()

    def open_file(self, token, contents):
        sublime.set_timeout(lambda: self.open_file_threaded(token, contents), 1)

    def open_file_threaded(self, token, contents):
        window = sublime.active_window()
        view = window.new_file()
        view.set_name(token)
        view.run_command("insert", {"characters": contents})

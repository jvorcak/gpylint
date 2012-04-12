from gi.repository import Gtk
from pylint.lint import PyLinter, MSG_TYPES

from gpylint.editor import GeditEditor, VimEditor
from gpylint.reporters import EditorReporter
from gpylint.settings import SettingsManager
from gpylint.helpers import get_pretty_name

class CodeWindow:
    '''
    Source code window
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''
    def __init__(self, filename, filepath):
        '''
        Initialize builder class and reads objects from xml
        '''
        self._builder = Gtk.Builder()
        self._builder.add_from_file('windows/code_window.xml')
        self._window = self._builder.get_object('code_window')
        self._code_frame = self._builder.get_object('code_frame')
        self._builder.connect_signals(self)
        self._filename = filename
        self._filepath = filepath
        self._editor = GeditEditor(filename, filepath)
        self._code_frame.add(self._editor.get_component())
        self._window.connect("delete-event", self.exit)
        self._window.set_title("%s : %s" % (filename, filepath))

    def show_all(self):
        self._window.show_all()

    def present(self):
        self._window.present()

    def run_pylint(self, parent):
        '''
        This method runs pylint agains the currently opened file
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        plugins = []
        pylintrc = None
        linter = PyLinter(reporter=EditorReporter(self._editor),
                pylintrc=pylintrc)
        linter.load_default_plugins()
        linter.load_plugin_modules(plugins)
        linter.read_config_file()
        linter.load_config_file()
        args = linter.load_command_line_configuration(\
                ['--reports=n', self._filepath])
        linter.check(args)

    def save(self, parent):
        raise NotImplementedError

    def set_lineno(self, lineno):
        self._editor.set_lineno(lineno)

    def exit(self, event, data):
        '''
        Needs to be unregistered from WindowManager when closing
        '''
        w = WindowManager()
        w.unregister(self._filepath)


class SettingsWindow(object):
    '''
    Settings window
    '''

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SettingsWindow, cls).__new__(\
                    cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file('windows/settings.xml')
        self._window = self._builder.get_object('settings_window')
        self._message_types_box = self._builder.get_object('message_types_box')
        self._main_notebook = self._builder.get_object('main_notebook')
        self._pylint_messages = self._builder.get_object('pylint_messages')

        sm = SettingsManager()
        for name, messages in sm.get_pylint_msgs().iteritems():
            self.add_section_tab(name, messages)

        self.load_pylint_general_page()
        self._builder.connect_signals(self)

    def show_pylint_general(self, button):
        self._main_notebook.set_current_page(0)

    def show_pylint_messages(self, button):
        self._main_notebook.set_current_page(1)


    def load_pylint_general_page(self):
        '''
        Loads the first settings page about Pylint
        Contains options to enable/disable message types
        '''
        box = self._message_types_box
        for k, v in MSG_TYPES.iteritems():
            box.add(Gtk.CheckButton(get_pretty_name(v)))

    def add_section_tab(self, name, messages):
        # init list store and set it as a model for treeview
        self._liststore = Gtk.ListStore(str, str, str, 'gboolean')
        treeview = Gtk.TreeView(self._liststore)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(treeview)
        self._pylint_messages.append_page(scrolled, Gtk.Label(get_pretty_name(name)))

        # init renderers
        self._code_renderer = Gtk.CellRendererText()
        self._msg_renderer = Gtk.CellRendererText()
        self._description_renderer = Gtk.CellRendererText()
        self._enabled_renderer = Gtk.CellRendererToggle()

        # init columns
        self._code_column = Gtk.TreeViewColumn('Code', self._code_renderer, \
                text=0)
        self._msg_column = Gtk.TreeViewColumn('Message', self._msg_renderer, \
                text=1)
        self._description_column = Gtk.TreeViewColumn('Description', \
                self._description_renderer, text=2)
        self._enabled_renderer = Gtk.TreeViewColumn('Enabled', \
                self._enabled_renderer, active=3)

        # expand message
        self._msg_column.set_expand(True)

        self._msg_column.set_resizable(True)
        self._description_column.set_resizable(True)

        # append columns to the tree view
        treeview.append_column(self._enabled_renderer)
        treeview.append_column(self._code_column)
        treeview.append_column(self._msg_column)
        treeview.append_column(self._description_column)

        for code, msg_tuple in messages.iteritems():
            msg, description = msg_tuple
            self._liststore.append([code, msg, description, True])

    def show_all(self):
        self._window.show_all()

class WindowManager(object):
    '''
    WindowManager is the manager of all opened coding windows, so there are no
    two windows opened with the same file
    Class is implemented as singleton
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''

    # singleton code
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WindowManager, cls).__new__(\
                    cls, *args, **kwargs)

        return cls._instance

    # class implementation
    _filepaths = {}

    def get_window(self, filename, filepath):
        if filepath not in self._filepaths.keys():
            self._filepaths[filepath] = CodeWindow(filename, filepath)
        return self._filepaths[filepath]

    def unregister(self, filepath):
        del self._filepaths[filepath]






import os
from gi.repository import Gtk

from gpylint.lint import GPyLinter
from gpylint.editor import GeditEditor, VimEditor
from gpylint.reporters import EditorReporter
from gpylint.settings.PylintMessagesManager import PylintMessagesManager
from gpylint.settings.GeneralSettingsManager import GeneralSettingsManager
from gpylint.helpers import get_pretty_name

pmm= PylintMessagesManager()
gsm = GeneralSettingsManager()

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
        self._error_image = self._builder.get_object('error_image')
        self._error_label = self._builder.get_object('error_label')
        self._statusbar = self._builder.get_object('statusbar')
        self._builder.connect_signals(self)
        self._filename = filename
        self._filepath = filepath
        self._editor = GeditEditor(filename, filepath, self._window, \
                (self._error_image, self._error_label, self._statusbar))
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
        linter = GPyLinter(reporter=EditorReporter(self._editor),
                pylintrc=pylintrc)
        linter.load_default_plugins()
        linter.load_plugin_modules(plugins)
        linter.read_config_file()
        linter.load_config_file()
        args = linter.load_command_line_configuration(\
                ['--reports=n', self._filepath])
        linter.check(args)

    def ignore_message_clicked(self, button):
        self._editor.ignore_message_clicked()

    def disable_message_clicked(self, button):
        self._editor.disable_message_clicked()
        pmm.ignore_code(self._editor.error_tag.msg_code)

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
        self._window.connect("delete-event", self.exit)

        for name, messages in pmm.get_pylint_msgs().iteritems():
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
        for msg, value in gsm.get_pylint_msgs_types().iteritems():
            button = Gtk.CheckButton(get_pretty_name(msg))
            button.connect('toggled', self.pylint_checkbox_toggled, msg)
            button.set_active(value)
            box.add(button)

    def pylint_checkbox_toggled(self, button, msg):
        gsm.save_boolean('pylint', msg, button.get_active())

    def add_section_tab(self, name, messages):
        PylintCheckerTab(self, name, messages)

    def show_all(self):
        self._window.show_all()

    def exit(self, event, data):
        pmm.save()
        gsm.save()

class PylintCheckerTab(object):

    def __init__(self, parent, name, messages):

        self.name = name

        # init list store and set it as a model for treeview
        # error_code, message, description, enabled

        self.liststore = Gtk.ListStore(str, str, str, 'gboolean')
        treeview = Gtk.TreeView(self.liststore)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(treeview)
        parent._pylint_messages.append_page(scrolled, \
                Gtk.Label(get_pretty_name(name)))

        # init renderers
        self._code_renderer = Gtk.CellRendererText()
        self._msg_renderer = Gtk.CellRendererText()
        self._description_renderer = Gtk.CellRendererText()
        self._enabled_renderer = Gtk.CellRendererToggle()
        self._enabled_renderer.connect('toggled', self.on_cell_toggled)

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
            # get value
            value = pmm.get_boolean(self.name, code)
            self.liststore.append([code, msg, description, value])

    def on_cell_toggled(self, widget, path):
        self.liststore[path][3] = not self.liststore[path][3]
        code, msg, description, value = self.liststore[path]
        pmm.save_boolean(self.name, code, value)


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

    def get_window(self, filepath):
        filename = os.path.relpath(filepath)
        if filepath not in self._filepaths.keys():
            self._filepaths[filepath] = CodeWindow(filename, filepath)
        return self._filepaths[filepath]

    def unregister(self, filepath):
        del self._filepaths[filepath]






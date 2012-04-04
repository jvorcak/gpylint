from gi.repository import Gtk
from pylint.lint import Run

from gpylint.editor import GeditEditor, VimEditor
from gpylint.reporters import EditorReporter


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
        Run(['--reports=n', self._filepath], reporter=EditorReporter(self._editor), \
                exit=False)

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






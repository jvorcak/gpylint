from gi.repository import Gtk, GtkSource, Vte, GLib

class Editor(object):

    """
    Class that is used for editing
    """

    def __init__(self, filename, filepath):
        self.filename = filename
        self.filepath = filepath
        self.open_file()

    def get_component(self):
        return self.component

    def add_message(self, sigle, line, col_offset, obj, msg):
        '''
        Displays pylint error message on the editor
        @author Jan Vorcak <vorcak@mail.muni.cz>
        @param sigle - pylint type of the error
        @param line - line number
        @param col_offset - offset
        @param obj - object in which the error occured
        @param msg - additional comment
        '''
        {
            'E': self.error_line,
            'W': self.warning_line,
            'C': self.convention_line,
            'I': self.info_line,
            'R': self.refactor_line,
            'F': self.fatal_line
            }[sigle](line-1, msg)

class VimEditor(Editor):

    """
    VimEditor
    """

    def open_file(self):
        self.component = Vte.Terminal()
        self.component.fork_command_full(Vte.PtyFlags.DEFAULT, None, ['vim',\
                self.filepath], [], GLib.SpawnFlags.SEARCH_PATH, None, None)
        self.component.show()

    def error_line(self, line_number, msg):
        pass

    def warning_line(self, line_number, msg):
        pass

    def convention_line(self, line_number, msg):
        pass

    def info_line(self, line_number, msg):
        pass

    def refactor_line(self, line_number, msg):
        pass

    def fatal_line(self, line_number, msg):
        pass


class GeditEditor(Editor):

    """
    GeditEditor
    """

    def __init__(self, filename, filepath):
        Editor.__init__(self, filename, filepath)
        self._error = self.ErrorWindow()

    def open_file(self):
        self.component = Gtk.ScrolledWindow()
        self.view = GtkSource.View()
        self.component.add(self.view)
        self.component.show()
        self.buff = GtkSource.Buffer()
        self.view.set_buffer(self.buff)
        manager = GtkSource.LanguageManager()
        self.buff.set_language(manager.guess_language(self.filename, None))

        self.view.connect('button-release-event', self.show_error_tag)

        # open file
        with open(self.filepath) as f:
            self.buff.set_text(f.read())
        self.view.show()

    def error_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='red')

    def warning_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='orange')

    def convention_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='orange')

    def info_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='orange')

    def refactor_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='orange')

    def fatal_line(self, line_number, msg):
        self._tag(line_number, msg, bc_color='red')

    def _tag(self, line, msg, bc_color='red'):

        start = self.buff.get_iter_at_line(line)
        end = self.buff.get_iter_at_line(line)
        end.forward_line()

        tag = self.ErrorTag(msg)
        tag.set_property('background', bc_color)

        self.buff.get_tag_table().add(tag)
        self.buff.apply_tag(tag, start, end)

    def show_error_tag(self, widget, event):
        '''
        This function is invoked on text view click
        Displays error if clicked on error tag
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        @param - widget
        @param - event
        '''
        self._error.window.hide()
        offset = self.buff.get_property('cursor-position')
        it = self.buff.get_iter_at_offset(offset)
        for x in it.get_tags():
            if hasattr(x, 'msg'):
                w, h = self._error.window.get_size()
                self._error.window.move(event.x_root - w/2, \
                        event.y_root - h - 5)
                self._error.set_msg(x.msg)
                self._error.window.show_all()

    class ErrorTag(Gtk.TextTag):

        def __init__(self, msg):
            Gtk.TextTag.__init__(self)
            self.msg = msg

    class ErrorWindow(Gtk.Window):

        def __init__(self):
            Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)
            builder = Gtk.Builder()
            builder.add_from_file('error_window.xml')
            self.window = builder.get_object('error_window')
            self.label = builder.get_object('error_msg')

        def set_msg(self, msg):
            self.label.set_text(msg)





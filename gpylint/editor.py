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
        }[sigle](line, msg)

class VimEditor(Editor):

    """
    VimEditor
    """

    def open_file(self):
        self.component = Vte.Terminal()
        self.component.fork_command_full(Vte.PtyFlags.DEFAULT, None, ['vim',\
                self.filepath], [], GLib.SpawnFlags.SEARCH_PATH, None, None)
        self.component.show()


class GeditEditor(Editor):

    """
    GeditEditor
    """

    def open_file(self):
        self.component = Gtk.ScrolledWindow()
        self.view = GtkSource.View()
        self.component.add(self.view)
        self.component.show()
        self.buff = GtkSource.Buffer()
        self.view.set_buffer(self.buff)
        manager = GtkSource.LanguageManager()
        self.buff.set_language(manager.guess_language(self.filename, None))

        # open file
        with open(self.filepath) as f:
            self.buff.set_text(f.read())
        self.view.show()

    def error_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='red')

    def warning_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='orange')

    def convention_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='orange')

    def info_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='orange')

    def refactor_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='orange')

    def fatal_line(self, line_number, msg):
        self.tag(line_number, msg, bc_color='red')

    def tag(self, line, msg, bc_color='red'):

        start = self.buff.get_iter_at_line(line)
        end = self.buff.get_iter_at_line(line)
        end.forward_line()

        tag = Gtk.TextTag()
        tag.set_property('background', bc_color)

        self.buff.get_tag_table().add(tag)
        self.buff.apply_tag(tag, start, end)


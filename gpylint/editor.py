from gi.repository import Gtk, GtkSource, Vte, GLib

class IgnoredTags(object):

    '''
    Manager for tags, that have been marked as ignored
    Responsible for (un)pickle these tags
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''

    ignored = {}

    def add_tag(self, filepath, error):
        if not self.ignored.has_key(filepath):
            self.ignored[filepath] = []
        if error not in self.ignored[filepath]:
            self.ignored[filepath].append(error)

    def get_values(self, filepath):
        if not self.ignored.has_key(filepath):
            self.ignored[filepath] = []
        return self.ignored[filepath]

    def load_errors(self, errors):
        for k in errors.keys():
            if not self.ignored.has_key(k):
                self.ignored[k] = []
            self.ignored[k].extend(errors[k])
            self.ignored[k] = list(set(self.ignored[k]))


ignored_tags = IgnoredTags()


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

        error = sigle, line-1, col_offset, obj, msg

        # needs to be improved
        if error in ignored_tags.get_values(self.filepath):
            return

        {
            'E': self.error_line,
            'W': self.warning_line,
            'C': self.convention_line,
            'I': self.info_line,
            'R': self.refactor_line,
            'F': self.fatal_line
        }[sigle](error)


class VimEditor(Editor):

    """
    VimEditor
    """

    def open_file(self):
        self.component = Vte.Terminal()
        self.component.fork_command_full(Vte.PtyFlags.DEFAULT, None, ['vim',\
                self.filepath], [], GLib.SpawnFlags.SEARCH_PATH, None, None)
        self.component.show()

    def error_line(self, error):
        pass

    def warning_line(self, error):
        pass

    def convention_line(self, error):
        pass

    def info_line(self, error):
        pass

    def refactor_line(self, error):
        pass

    def fatal_line(self, error):
        pass


class GeditEditor(Editor):

    """
    GeditEditor
    """

    def __init__(self, filename, filepath):
        Editor.__init__(self, filename, filepath)
        self._error = self.ErrorWindow(filepath)

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

    def error_line(self, error):
        self._tag(error, bc_color='red')

    def warning_line(self, error):
        self._tag(error, bc_color='orange')

    def convention_line(self, error):
        self._tag(error, bc_color='orange')

    def info_line(self, error):
        self._tag(error, bc_color='orange')

    def refactor_line(self, error):
        self._tag(error, bc_color='orange')

    def fatal_line(self, error):
        self._tag(error, bc_color='red')

    def _tag(self, error, bc_color='red'):

        sigle, line, col_offset, obj, msg = error

        start = self.buff.get_iter_at_line(line)
        end = self.buff.get_iter_at_line(line)
        end.forward_line()

        tag = self.ErrorTag(error, self.buff.get_tag_table())
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
            if hasattr(x, 'error'):
                w, h = self._error.window.get_size()
                self._error.window.move(event.x_root - w/2, \
                        event.y_root - h - 5)
                self._error.set_error_tag(x)
                self._error.window.show_all()

    class ErrorTag(Gtk.TextTag):

        def __init__(self, error, tag_table):
            Gtk.TextTag.__init__(self)
            # sigle, line, col_offset, obj, msg = error
            self.error = error
            self._tag_table = tag_table

        msg = property(lambda self: self.error[4])

        def __cmp__(self, other):
            if id(self) == id(other):
                return True

            if not isinstance(other, self.__class__):
                return False

            if self.msg == other.msg and self.sigle == other.sigle and\
                    self.obj == self.obj:
                return True

            return False

        def disable(self):
            self._tag_table.remove(self)

    class ErrorWindow(Gtk.Window):

        def __init__(self, filepath):
            Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)
            builder = Gtk.Builder()
            builder.add_from_file('error_window.xml')
            self.window = builder.get_object('error_window')
            self.label = builder.get_object('error_msg')
            builder.connect_signals(self)

            self._filepath = filepath

        def set_error_tag(self, error):
            self.error_tag = error
            self.label.set_text(error.msg)

        def ignore_tag(self, button):

            self.error_tag.disable()

            if self.error_tag.error not in \
                    ignored_tags.get_values(self._filepath):
                ignored_tags.add_tag(self._filepath, self.error_tag.error)

            self.window.hide()


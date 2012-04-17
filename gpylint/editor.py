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

    def add_message(self, msg_id, line, col_offset, obj, msg, ignored):
        '''
        Displays pylint error message on the editor
        @author Jan Vorcak <vorcak@mail.muni.cz>
        @param msg_id - pylint code of the error
        @param line - line number
        @param col_offset - offset
        @param obj - object in which the error occured
        @param msg - additional comment
        '''
        sigle = msg_id[0]
        error = sigle, msg_id, line-1, col_offset, obj, msg, ignored

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

    def error_line(self, error):
        raise NotImplementedError

    def warning_line(self, error):
        raise NotImplementedError

    def convention_line(self, error):
        raise NotImplementedError

    def info_line(self, error):
        raise NotImplementedError

    def refactor_line(self, error):
        raise NotImplementedError

    def fatal_line(self, error):
        raise NotImplementedError

    def set_lineno(self, lineno):
        raise NotImplementedError

    def show_statistics(self, linter):
        raise NotImplementedError

    def ignore_current_tag(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

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

    def show_statistics(self, linter):
        pass

    def ignore_current_tag(self):
        pass

    def save(self):
        pass

    def set_lineno(self, lineno):
        pass

class GeditEditor(Editor):

    """
    GeditEditor
    """

    def __init__(self, filename, filepath, code_window):
        Editor.__init__(self, filename, filepath)
        self._window = code_window._window
        self._error_image = code_window._error_image
        self._error_label = code_window._error_label
        self._status_bar = code_window._statusbar
        self._error_box = code_window._error_box
        self._pylint_button = code_window._pylint_button
        self._save_button = code_window._save_button
        self._save_button.set_sensitive(False)

    def open_file(self):
        self.component = Gtk.ScrolledWindow()
        self.view = GtkSource.View()

        # set view properties
        self.view.set_property('highlight-current-line', True)
        self.view.set_property('show-line-numbers', True)
        self.view.set_property('draw-spaces', True)
        self.view.set_property('insert-spaces-instead-of-tabs', True)
        self.view.set_property('tab-width', 4)

        self.component.add(self.view)
        self.component.show()
        self.buff = GtkSource.Buffer()

        self.buff.connect('changed', self.changed)

        self.view.set_buffer(self.buff)
        manager = GtkSource.LanguageManager()
        self.buff.set_language(manager.guess_language(self.filename, None))

        self.view.connect('button-release-event', self.show_error_tag)
        # open file
        with open(self.filepath) as f:
            self.buff.set_text(f.read())
        self.view.show()

    def changed(self, signal):
        if self.buff.get_modified():
            self._save_button.set_sensitive(True)

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

        sigle, msg_id, line, col_offset, obj, msg, ignored = error

        if ignored:
            return

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
        offset = self.buff.get_property('cursor-position')
        it = self.buff.get_iter_at_offset(offset)

        self._error_box.set_visible(False)

        for x in it.get_tags():
            if hasattr(x, 'error'):
                self._error_box.set_visible(True)

                self.error_tag = x
                stock_name = \
                {
                 'C': Gtk.STOCK_DIALOG_WARNING,
                 'E': Gtk.STOCK_DIALOG_ERROR,
                 'F': Gtk.STOCK_DIALOG_ERROR,
                 'I': Gtk.STOCK_DIALOG_INFO,
                 'R': Gtk.STOCK_DIALOG_WARNING,
                 'W': Gtk.STOCK_DIALOG_WARNING,
                }[x.msg_type]

                self._error_image.set_from_stock(stock_name, \
                        Gtk.IconSize.SMALL_TOOLBAR)
                self._error_label.set_text('%s : %s' % (x.msg_code, x.msg))

    def show_statistics(self, statistics):
        total_errors = statistics['msgs_count']
        total_ignored = statistics['ignored_msgs_count']
        self._status_bar.push(0, \
                '%d errors and warnings, %d blocked' % \
                (total_errors, total_ignored))

    def ignore_current_tag(self):
        if self.error_tag.error not in \
               ignored_tags.get_values(self.filepath):
           ignored_tags.add_tag(self.filepath, \
                   self.error_tag.error)

    def clear_tags(self):
        self.buff.get_tag_table().foreach(self._clear_tags, None)

    def _clear_tags(editor, tag, data):
        if hasattr(tag, 'disable'):
            tag.disable()

    def save(self):
        self._save_button.set_sensitive(False)
        with open(self.filepath, 'w') as f:
            f.write(self.buff.get_text(\
                    self.buff.get_start_iter(),
                    self.buff.get_end_iter(), True))
            self.buff.set_modified(False)

    class ErrorTag(Gtk.TextTag):

        def __init__(self, error, tag_table):
            Gtk.TextTag.__init__(self)
            # sigle, line, col_offset, obj, msg = error
            self.error = error
            self._tag_table = tag_table

        # self error example
        # ('C', 'C0111', 31, 4, 'CodeWindow.present', 'Missing docstring')

        msg_type = property(lambda self: self.error[0])
        msg_code = property(lambda self: self.error[1])
        msg = property(lambda self: self.error[5])

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

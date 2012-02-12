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

    def show_pylint_output(self, output):
        pass

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

    def show_pylint_output(self, output):
        for message in output:
            type, location, msg = message
            line, location = location.split(',')
            self.tag(int(line), msg)

    def tag(self, line, msg, bc_color="red"):

        start = self.buff.get_iter_at_line(line)
        end = self.buff.get_iter_at_line(line)
        end.forward_line()

        tag = Gtk.TextTag()
        tag.set_property("background", "red")

        self.buff.get_tag_table().add(tag)
        self.buff.apply_tag(tag, start, end)


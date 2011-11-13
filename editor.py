import pango

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


    def tag(self):
        self.tag = Gtk.TextTag()
        self.tag.set_property("style", pango.STYLE_ITALIC)
        self.tag.set_property("background", "red")
        self.buff.get_tag_table().add(self.tag)
        start = self.buff.get_iter_at_offset(2)
        end = self.buff.get_iter_at_offset(5)
        self.buff.apply_tag(self.tag, start, end)


from gi.repository import Gtk

from gaphas.tool import Tool
from gpylint.windows import WindowManager

wm = WindowManager()

class OpenEditorTool(Tool):

    def __init__(self, view=None):
        super(OpenEditorTool, self).__init__(view)

    def on_double_click(self, event):
        class_box = self.view.hovered_item
        if not hasattr(class_box, 'filepath'):
            # TODO add parent instead of None
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK, 'Can\'t show source code')
            dialog.format_secondary_text('This class doesn\'t have source' + \
                    ' code available')
            dialog.run()
            dialog.destroy()

        window = wm.get_window(class_box.filepath)
        window.show_all()
        window.present()



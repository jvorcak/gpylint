from gaphas.tool import Tool
from gpylint.windows import WindowManager

wm = WindowManager()

class OpenEditorTool(Tool):

    def __init__(self, view=None):
        super(OpenEditorTool, self).__init__(view)

    def on_double_click(self, event):
        class_box = self.view.hovered_item
        if class_box:
            window = wm.get_window(class_box.filepath, class_box.filepath)
            window.show_all()
            window.present()



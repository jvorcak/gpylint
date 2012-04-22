import sys

from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter
from gpylint.filters import SettingsFilter
from gpylint.editor import ignored_tags
from gpylint.canvas import CanvasContext

settings_filter = SettingsFilter()

def is_ignored(values, msg_id, line, col_offset, obj, msg):
    for error in values:
        _sigle, _msg_id, _line, _col_offset, _obj, _msg, _ignored = error
        if _msg_id == msg_id and _col_offset == col_offset and \
                _obj == obj and _msg == msg:
            return True
    return False

class EditorReporter(BaseReporter):
    '''
    Shows pylint messages directly to the source code
    '''

    __implements__ = IReporter
    extension = 'txt'

    def __init__(self, editor, output=sys.stdout):
        BaseReporter.__init__(self, output)
        self._editor = editor
        self._ignored_msgs_count = 0
        self._msgs_count = 0

    def add_message(self, msg_id, location, msg):
        """manage message of different type and in the context of path"""
        module, obj, line, col_offset = location[1:]

        ignored = is_ignored(ignored_tags.get_values(\
                self._editor.filepath), msg_id, line, col_offset, obj, msg)

        ignored = ignored or settings_filter.code_is_ignored(msg_id)

        if ignored:
            self._ignored_msgs_count += 1
        else:
            self._msgs_count += 1

        self._editor.add_message(msg_id, line, col_offset, obj, msg, ignored)

    def display_results(self, sect):
        statistics = {}
        statistics['ignored_msgs_count'] = self._ignored_msgs_count
        statistics['msgs_count'] = self._msgs_count
        self._editor.show_statistics(statistics)

class CanvasReporter(BaseReporter):
    '''
    Shows error on the canvas
    '''

    __implements__ = IReporter

    def __init__(self):
        BaseReporter.__init__(self, sys.stdout)
        self.context = CanvasContext().dictionary
        for class_box in self.context.values():
            class_box.clear_errors()

    def add_message(self, msg_id, location, msg):

        filepath, module, obj, line, col_offset = location
        if settings_filter.code_is_ignored(msg_id) or \
                is_ignored(ignored_tags.get_values(filepath), \
                           msg_id, line, col_offset, obj, msg):
            return

        key = (location[0], obj.split('.')[0]) # (filepath, objectname)
        if key in self.context:
            self.context[key].add_error(msg_id)

    def display_results(self, sect):
       for class_box in self.context.values():
           class_box.request_update()

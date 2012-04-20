import sys

from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter
from gpylint.filters import SettingsFilter
from gpylint.editor import ignored_tags

settings_filter = SettingsFilter()

class EditorReporter(BaseReporter):
    '''
    shows pylint messages directly to the source code
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

        ignored = self.is_ignored(ignored_tags.get_values(\
                self._editor.filepath), msg_id, line, col_offset, obj, msg)

        ignored = ignored or settings_filter.code_is_ignored(msg_id)

        if ignored:
            self._ignored_msgs_count += 1
        else:
            self._msgs_count += 1

        self._editor.add_message(msg_id, line, col_offset, obj, msg, ignored)

    def is_ignored(self, values, msg_id, line, col_offset, obj, msg):
        for error in values:
            _sigle, _msg_id, _line, _col_offset, _obj, _msg, _ignored = error
            if _msg_id == msg_id and _col_offset == col_offset and \
                    _obj == obj and _msg == msg:
                return True
        return False

    def display_results(self, sect):
        statistics = {}
        statistics['ignored_msgs_count'] = self._ignored_msgs_count
        statistics['msgs_count'] = self._msgs_count
        self._editor.show_statistics(statistics)


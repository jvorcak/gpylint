import sys

from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter

class EditorReporter(BaseReporter):
    '''
    shows pylint messages directly to the source code
    '''

    __implements__ = IReporter
    extension = 'txt'

    def __init__(self, editor, output=sys.stdout):
        BaseReporter.__init__(self, output)
        self._editor = editor

    def add_message(self, msg_id, location, msg):
        """manage message of different type and in the context of path"""
        module, obj, line, col_offset = location[1:]
        if self.include_ids:
            sigle = msg_id
        else:
            sigle = msg_id[0]

        self._editor.add_message(sigle, line, col_offset, obj, msg)


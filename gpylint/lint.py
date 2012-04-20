from gi.repository import Gdk
from threading import Thread
from StringIO import StringIO

from pylint.lint import PyLinter
from pylint.utils import PyLintASTWalker
from pylint.interfaces import IASTNGChecker, IRawChecker

from logilab.common.interface import implements
from logilab.astng.builder import ASTNGBuilder
from logilab.astng import MANAGER

class GPyLinter(Thread):

    def __init(self):
        super(GPyLinter, self).__init__()

    def init_linter(self, reporter, pylintrc):
        self.linter = PyLinter(reporter=reporter, pylintrc=pylintrc)

    def load_default_plugins(self):
        self.linter.load_default_plugins()

    def read_config_file(self):
        self.linter.read_config_file()

    def load_plugin_modules(self, plugins):
        self.linter.load_plugin_modules(plugins)

    def load_config_file(self):
        self.linter.load_config_file()

    def set_buffer(self, buff):
        self.buff = buff

    def set_scanning_items(self, label, spinner):
        self.label = label
        self.spinner = spinner

    def run(self):
        self._check_text_buffer(self.buff)

    def _check_text_buffer(self, buff):
        '''
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        Run pylint on input from GtkTextBuffer
        @param buff - instance of GtkTextBuffer to be checked
        '''

#        Gdk.threads_init()
#        self.spinner.set_visible(True)
#        self.label.set_visible(True)
#        Gdk.threads_leave()

        walker = PyLintASTWalker(self.linter)

        # prepare checkers
        checkers = self.linter.prepare_checkers()
        rawcheckers = [c for c in checkers if implements(c, IRawChecker)
                       and c is not self]
        for checker in checkers:
            checker.open()
            if implements(checker, IASTNGChecker):
                walker.add_checker(checker)
        source = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), \
                True)

        self.linter.base_name = 'textbuffername'
        self.linter.base_file = 'textbufferpath'

        self.linter.set_current_module(self.linter.base_name, \
                self.linter.base_file)

        astng = ASTNGBuilder(MANAGER).string_build(source, modname='buffer')
        astng.file_stream = StringIO(source)
        astng.file_encoding = 'utf8'
        if astng is None:
            return
        self.linter.current_name = self.linter.base_name

        self.linter.check_astng_module(astng, walker, rawcheckers)
        self.linter.stats['statement'] = walker.nbstatements
        checkers.reverse()
        for checker in checkers:
            checker.close()

#        Gdk.threads_init()
#        self.spinner.set_visible(False)
#        self.label.set_visible(False)
#        Gdk.threads_leave()

from pylint.lint import PyLinter
from pylint.utils import PyLintASTWalker
from pylint.interfaces import IASTNGChecker, IRawChecker

from logilab.common.interface import implements
from logilab.astng.builder import ASTNGBuilder
from logilab.astng import MANAGER
from StringIO import StringIO

class GPyLinter(PyLinter):

    def check_text_buffer(self, buff):
        '''
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        Run pylint on input from GtkTextBuffer
        @param buff - instance of GtkTextBuffer to be checked
        '''
        walker = PyLintASTWalker(self)

        # prepare checkers
        checkers = self.prepare_checkers()
        rawcheckers = [c for c in checkers if implements(c, IRawChecker)
                       and c is not self]
        for checker in checkers:
            checker.open()
            if implements(checker, IASTNGChecker):
                walker.add_checker(checker)
        source = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), \
                True)

        self.base_name = 'textbuffername'
        self.base_file = 'textbufferpath'

        self.set_current_module(self.base_name, self.base_file)

        astng = ASTNGBuilder(MANAGER).string_build(source, modname='buffer')
        astng.file_stream = StringIO(source)
        astng.file_encoding = 'utf8'
        if astng is None:
            return
        self.current_name = self.base_name

        self.check_astng_module(astng, walker, rawcheckers)
        self.stats['statement'] = walker.nbstatements
        checkers.reverse()
        for checker in checkers:
            checker.close()


    def close(self):
        self.reporter.close()

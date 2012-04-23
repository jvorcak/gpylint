import os
from threading import Thread
from StringIO import StringIO

from pylint.lint import PyLinter
from pylint.utils import PyLintASTWalker, expand_modules
from pylint.interfaces import IASTNGChecker, IRawChecker

from logilab.common.interface import implements
from logilab.astng.builder import ASTNGBuilder
from logilab.astng import MANAGER

from gpylint.scanner import BlackList

class IgnoreLinter(PyLinter):

    '''
    Class extends PyLinter functionality and adds filtering functionality
    '''

    i = 0.
    files_to_process = property(lambda x: len(x.result))

    def expand_files(self, modules):
        """get modules and errors from a list of modules and handle errors
        """
        result, errors = expand_modules(modules, [''])
        self.result = result = filter(self.blacklist_result, result)
        for error in errors:
            message = modname = error["mod"]
            key = error["key"]
            self.set_current_module(modname)
            if key == "F0001":
                message = str(error["ex"]).replace(os.getcwd() + os.sep, '')
            self.add_message(key, args=message)
        return result

    def blacklist_result(self, item):
        return not any([item['path'].startswith(ignored_item) \
             for ignored_item in BlackList().blacklist])

    def set_current_module(self, modname, filepath=None):
        super(IgnoreLinter, self).set_current_module(modname, filepath)
        self.i += 1
        self.reporter.update_progressbar(self.i/self.files_to_process)

class GPyLinter(Thread):

    linter = None

    def __init__(self):
        super(GPyLinter, self).__init__()

    def init_linter(self, reporter, pylintrc):
        pass

    def load_default_plugins(self):
        self.linter.load_default_plugins()

    def read_config_file(self):
        self.linter.read_config_file()

    def load_plugin_modules(self, plugins):
        self.linter.load_plugin_modules(plugins)

    def load_config_file(self):
        self.linter.load_config_file()

    def run(self):
        pass

class ProjectLinter(GPyLinter):
    
    def init_linter(self, reporter, pylintrc):
        self.linter = IgnoreLinter(reporter=reporter, pylintrc=pylintrc)
    
    def set_project_path(self, project_path):
        self.project_path = project_path

    def run(self):
        args = self.linter.load_command_line_configuration([self.project_path])
        self.linter.check(args)

class TextBufferLinter(GPyLinter):

    '''
    Linter for running pylint on TextBuffer instance
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''

    def init_linter(self, reporter, pylintrc):
        self.linter = PyLinter(reporter=reporter, pylintrc=pylintrc)

    def set_buffer(self, buff):
        self.buff = buff

    def set_scanning_items(self, label, spinner):
        self.label = label
        self.spinner = spinner

    def run(self):
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
        source = self.buff.get_text(self.buff.get_start_iter(), \
                self.buff.get_end_iter(), True)

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

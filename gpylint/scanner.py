import sys, os

from gi.repository import Gdk
from threading import Thread
from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import ASTNGManager
from logilab.astng.inspector import Linker

from pylint.pyreverse.main import OPTIONS
from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse.utils import insert_default_options

import writer

class ScannerCommand(ConfigurationMixIn):
    """base class providing common behaviour for pyreverse commands"""

    options = OPTIONS

    def __init__(self, view, args, callback):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        self.view = view
        self.callback = callback
        self.run(args)

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        # insert current working directory to the python path to recognize
        # dependencies to local modules even if cwd is not in the PYTHONPATH
        sys.path.insert(0, os.getcwd())
        try:
            project = self.manager.project_from_files(args, black_list= \
                    map(os.path.relpath, ScanProject.blacklist))
            linker = Linker(project, tag=True)
            handler = DiadefsHandler(self.config)
            diadefs = handler.get_diadefs(project, linker)
        finally:
            sys.path.pop(0)

        # filter just classes (not packages) for now
        diadefs = filter(lambda x: x.TYPE == 'class', diadefs)

        # update GUI
        Gdk.threads_init()
        self.callback()
        Gdk.threads_leave()
        writer.CanvasWriter(self.view, self.config).write(diadefs)

class ScanProject(Thread):

    blacklist = []

    """pyreverse main class"""
    def __init__(self, view, args, callback):
        super(ScanProject, self).__init__()
        """run pyreverse"""
        self.view = view
        self.args = args
        self.callback = callback
    def run(self):
        ScannerCommand(self.view, self.args, self.callback)


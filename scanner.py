import sys, os
from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import ASTNGManager
from logilab.astng.inspector import Linker

from pylint.pyreverse.diadefslib import DiadefsHandler
import writer
from pylint.pyreverse.utils import insert_default_options

OPTIONS = (
("filter-mode",
    dict(short='f', default='PUB_ONLY', dest='mode', type='string',
    action='store', metavar='<mode>', 
    help="""filter attributes and functions according to
    <mode>. Correct modes are :
                            'PUB_ONLY' filter all non public attributes
                                [DEFAULT], equivalent to PRIVATE+SPECIAL_A
                            'ALL' no filter
                            'SPECIAL' filter Python special functions
                                except constructor
                            'OTHER' filter protected and private
                                attributes""")),

("class",
dict(short='c', action="append", metavar="<class>", dest="classes", default=[],
    help="create a class diagram with all classes related to <class>;\
 this uses by default the options -ASmy")),

("show-ancestors",
dict(short="a",  action="store", metavar='<ancestor>', type='int',
    help='show <ancestor> generations of ancestor classes not in <projects>')),
("all-ancestors",
dict(short="A", default=None,
    help="show all ancestors off all classes in <projects>") ),
("show-associated",
dict(short='s', action="store", metavar='<ass_level>', type='int',
    help='show <ass_level> levels of associated classes not in <projects>')),
("all-associated",
dict(short='S', default=None,
    help='show recursively all associated off all associated classes')),

("show-builtin",
dict(short="b", action="store_true", default=False,
    help='include builtin objects in representation of classes')),

("module-names",
dict(short="m", default=None, type='yn', metavar='[yn]',
    help='include module name in representation of classes')),
# TODO : generate dependencies like in pylint
#("package-dependencies",
#dict(short="M", action="store", metavar='<package_depth>', type='int',
    #help='show <package_depth> module dependencies beyond modules in \
#<projects> (for the package diagram)')),
("only-classnames",
dict(short='k', action="store_true", default=False,
    help="don't show attributes and methods in the class boxes; \
this disables -f values")),
("output", dict(short="o", dest="output_format", action="store",
                 default="dot", metavar="<format>",
                help="create a *.<format> output file if format available.")),
#("ignore", {"dest":"blacklist", "default":("gaphas",)}),
)
# FIXME : quiet mode
#( ('quiet', 
                #dict(help='run quietly', action='store_true', short='q')), )

class ScannerCommand(ConfigurationMixIn):
    """base class providing common behaviour for pyreverse commands"""

    options = OPTIONS

    def __init__(self, view, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        self.view = view
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
            project = self.manager.project_from_files(args, black_list=['gaphas']) # tmp solution, need to add popupmenu
            linker = Linker(project, tag=True)
            handler = DiadefsHandler(self.config)
            diadefs = handler.get_diadefs(project, linker)
        finally:
            sys.path.pop(0)

        # filter just classes (not packages) for now
        diadefs = filter(lambda x: x.TYPE == 'class', diadefs)

        writer.DotWriter(self.view, self.config).write(diadefs)


class ScanProject:
    """pyreverse main class"""
    def __init__(self, view, args):
        """run pyreverse"""
        ScannerCommand(view, args)


# -*- coding: utf-8 -*-
"""
Utilities for creating diagram on canvas
"""

from logilab.common.graph import DotBackend

from pylint.pyreverse.writer import DiagramWriter
from pylint.pyreverse.utils import is_exception

class DotWriter(DiagramWriter):
    """write dot graphs from a diagram definition and a project
    """

    def __init__(self, config):
        styles = [dict(arrowtail='none', arrowhead="open"), 
                  dict(arrowtail = "none", arrowhead='empty'), 
                  dict(arrowtail="node", arrowhead='empty', style='dashed'),
                  dict(fontcolor='green', arrowtail='none',
                       arrowhead='diamond', style='solid') ]
        DiagramWriter.__init__(self, config, styles)

    def set_printer(self, file_name, basename):
        """initialize DotWriter and add options for layout.
        """
        layout = dict(rankdir="BT")
        self.printer = DotBackend(basename, additionnal_param=layout)
        self.file_name = file_name

    def get_title(self, obj):
        """get project title"""
        return obj.title

    def get_values(self, obj):
        """get label and shape for classes.
        
        The label contains all attributes and methods
        """
        label =  obj.title
        if obj.shape == 'interface':
            label = "«interface»\\n%s" % label
        if not self.config.only_classnames:
            label = "%s|%s\l|" % (label,  r"\l".join(obj.attrs) )
            for func in obj.methods:
                label = r'%s%s()\l' % (label, func.name)
            label = '{%s}' % label
        if is_exception(obj.node):
            return dict(fontcolor="red", label=label, shape="record")
        return dict(label=label, shape="record")

    def close_graph(self):
        """print the dot graph into <file_name>"""
        self.printer.generate(self.file_name)



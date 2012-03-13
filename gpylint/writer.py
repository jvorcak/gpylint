# -*- coding: utf-8 -*-
"""
Utilities for creating diagram on canvas
"""

from pylint.pyreverse.writer import DiagramWriter
from pylint.pyreverse.utils import is_exception
from igraph import Graph

from gpylint.canvas import ClassBox, set_association

class CanvasBackend:
    """ Canvas backend """

    def __init__(self, view):
        self.view = view
        self.nodes = []
        self.edges = []
        self.graph = None

    def emit_node(self, name, **props):
        '''
        Append node with given properties to the list
        '''
        label = props['label']
        box = ClassBox(label)

        self.nodes.append({'name' : name, 'box' : box })

    def emit_edge(self, name1, name2, **props):
        '''
        Append edge with give properties to the list
        '''
        self.edges.append((name1, name2, props))

    def generate(self, filename):
        '''
        Displays the graph on the canvas
        Uses python-igraph fruchterman-reingold algorithm to decide about
        position of the nodes, then draw these nodes on the canvas and
        draw connections between them
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        self.graph = Graph(len(self.nodes))
        self.graph.vs['name'] = [node['name'] for node in self.nodes]
        self.graph.vs['box'] = [node['box'] for node in self.nodes]

        for name1, name2, props in self.edges:
            v1 = self.graph.vs.select(name_eq=name1)
            v2 = self.graph.vs.select(name_eq=name2)
            self.graph.add_edges((v1[0].index, v2[0].index))

        for i, v in enumerate(self.graph.layout_grid_fruchterman_reingold()):
            x, y = v
            box = self.graph.vs[i]['box']
            box.matrix.translate((x+2)*40, (y+2)*40)
            print box, " at ", x+2, y+2
            self.view.canvas.add(box)

        for name1, name2, props in self.edges:
            v1 = self.graph.vs.select(name_eq=name1)['box'][0]
            v2 = self.graph.vs.select(name_eq=name2)['box'][0]

            set_association(self.view.canvas, v2, v1, props)


class CanvasWriter(DiagramWriter):
    """write canvas graphs from a diagram definition
    """

    def __init__(self, canvas, config):
        self.canvas = canvas
        styles = [dict(arrowtail='none', arrowhead="open"), 
                  dict(arrowtail="none", arrowhead='empty'), 
                  dict(arrowtail="node", arrowhead='empty', style='dashed'),
                  dict(fontcolor='green', arrowtail='none',
                       arrowhead='diamond', style='solid') ]
        DiagramWriter.__init__(self, config, styles)

    def set_printer(self, file_name, basename):
        """initialize CanvasBackend and add options for layout.
        """
        self.printer = CanvasBackend(self.canvas)
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
#        if not self.config.only_classnames:
#            label = "%s|%s\l|" % (label,  r"\l".join(obj.attrs) )
#            for func in obj.methods:
#                label = r'%s%s()\l' % (label, func.name)
#            label = '{%s}' % label
        if is_exception(obj.node):
            return dict(fontcolor="red", label=label, shape="record")
        return dict(label=label, shape="record")

    def close_graph(self):
        """print the graph into the canvas"""
        self.printer.generate(self.file_name)



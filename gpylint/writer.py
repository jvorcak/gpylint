# -*- coding: utf-8 -*-
"""
Utilities for creating diagram on canvas
"""

from logilab.common.graph import DotBackend
from pylint.pyreverse.writer import DiagramWriter
import gv

from gpylint.canvas.items import ClassBox
from gpylint.canvas import set_association, CanvasContext

class CanvasBackend(DotBackend):
    """ Canvas backend """

    def __init__(self, view):
        super(CanvasBackend, self).__init__('basename')
        self.view = view
        self.nodes = []
        self.edges = []
        self.graph = None

    def generate(self, filename):
        '''
        Displays the graph on the canvas
        Uses python-igraph fruchterman-reingold algorithm to decide about
        position of the nodes, then draw these nodes on the canvas and
        draw connections between them
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''

        g = gv.readstring(self.source)
        gv.layout(g, 'dot')
        gv.render(g)

        context = CanvasContext().dictionary

        node = gv.firstnode(g)
        while node is not None:
            props = {
                    'filepath' : gv.getv(node, 'filepath'),
                    'title' : gv.getv(node, 'label'),
                    'lineno' : gv.getv(node, 'lineno'),
                    }
            pos = gv.getv(node, 'pos').split(',')
            width = gv.getv(node, 'width')
            height = gv.getv(node, 'height')
            x, y = map(int, pos)
            class_box = ClassBox(props, width, height)
            class_box.matrix.translate(x, y)
            self.view.canvas.add(class_box)
            context[(props['filepath'], props['title'])] = class_box
            node = gv.nextnode(g, node)

        edge = gv.firstedge(g)
        while edge is not None:
            props = {
                    'arrowhead' : gv.getv(edge, 'arrowhead'),
                    'arrowtail' : gv.getv(edge, 'arrowtail'),
                    }

            head = gv.headof(edge)
            tail = gv.tailof(edge)
            head_str = (gv.getv(head, 'filepath'), gv.getv(head, 'label'))
            tail_str = (gv.getv(tail, 'filepath'), gv.getv(tail, 'label'))
            context[head_str]
            context[tail_str]

            edge = gv.nextedge(g, edge)
            set_association(self.view.canvas, context[head_str], \
                    context[tail_str], props)


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
        '''
        Parse dictionary from object depending on the object type
        '''

        d = dict()
        d['label'] = obj.title

        if obj.shape == 'class' and hasattr(obj.node.parent, 'file'):
            d['filepath'] = obj.node.parent.file
            d['lineno'] = obj.node.lineno

        return d

    def close_graph(self):
        """print the graph into the canvas"""
        self.printer.generate(self.file_name)



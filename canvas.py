'''
This modules is responsible for drawing classes and modules on canvas
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

from gaphas.item import Element, NW, Line
from gaphas.connector import Handle, PointPort
from gaphas.solver import STRONG
from gaphas.util import text_align
from gaphas.aspect import Connector, ConnectionSink

class Box(Element):
    """ A Box has 5 handles:
     NW +---+ NE
        | + | <- central handle
     SW +---+ SE
    """

    def __init__(self, width=10, height=10):
        super(Box, self).__init__(width, height)
        self._central_handle = Handle(strength=STRONG)
        self._central_handle.visible = False
        self._central_handle.pos = width / 2.0, height / 2.0
        self._ports.append(PointPort(self._central_handle.pos))
        self._handles.append(self._central_handle)

    def draw(self, context):
        c = context.cairo
        nw = self._handles[NW].pos
        c.rectangle(nw.x, nw.y, self.width, self.height)
        if context.hovered:
            c.set_source_rgba(.8,.8,1, .8)
        else:
            c.set_source_rgba(1,1,1, .8)
        c.fill_preserve()
        c.set_source_rgb(0,0,0.8)
        c.stroke()


class ClassBox(Box):

    def __init__(self, cls, width=100, height=100):
        super(ClassBox, self).__init__(width, height)
        self.cls = cls

    def draw(self, context):
        super(ClassBox, self).draw(context)
        c = context.cairo
        x,y = self._central_handle.pos
        text_align(c, x, y, str(self.cls.__class__), 0, 0)

    def set_superclass(self, superclass):
        '''
        Make connection between this ClassBox and given superclass
        @author Jan Vorcak <vorcak@mail.muni.cz>
        @param superclass - classbox of superclass
        '''

        line = Line()
        line.matrix.translate(240, 240)
        for handle in line.handles():
            handle.visible = False
        self._canvas.add(line)
        connector = Connector(line, line.handles()[0])
        connector.connect(ConnectionSink(superclass, superclass.ports()[4]))

        connector = Connector(line, line.handles()[1])
        connector.connect(ConnectionSink(self, self.ports()[4]))

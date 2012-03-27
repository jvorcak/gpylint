'''
This modules is responsible for drawing classes and modules on canvas
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

import math

from gaphas.item import Element, NW, SW, NE, SE, Line
from gaphas.connector import Handle, PointPort
from gaphas.solver import STRONG
from gaphas.util import text_align
from gaphas.aspect import Connector, ConnectionSink
from gaphas.constraint import EquationConstraint, LineConstraint

class Box(Element):
    """ A Box has 5 handles:
     NW +---+ NE
        | + | <- central handle
     SW +---+ SE
    """

    def __init__(self, width=10, height=10):
        super(Box, self).__init__(width, height)

        for handle in self._handles:
            handle.visible = False
            handle.moveable = False

        self._central_handle = Handle(strength=STRONG)
        self._central_handle.visible = True
        self._central_handle.pos = width / 2.0, height / 2.0
        self._ports.append(PointPort(self._central_handle.pos))
        self._handles.append(self._central_handle)

    def get_centeral_position(self):
        return self._central_handle.pos

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


class AssociationLine(Line):

    def __init__(self, props):
        '''
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        @param props - properties passed to the line from scanner
        '''
        super(AssociationLine, self).__init__()
        self.props = props

    def draw(self, context):
        super(AssociationLine, self).draw(context)

        {
            'diamond': self.draw_head_composite,
            'empty': self.draw_head_none
        }[self.props['arrowhead']](context)

    def draw_head_none(self, context):
        """
        Draw an 'x' on the line end to indicate no navigability at
        association head.
        """
        cr = context.cairo
        cr.move_to(6, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()
        cr.move_to(0, 0)


    def draw_tail_none(self, context):
        """
        Draw an 'x' on the line end to indicate no navigability at
        association tail.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.move_to(6, -4)
        cr.rel_line_to(8, 8)
        cr.rel_move_to(0, -8)
        cr.rel_line_to(-8, 8)
        cr.stroke()


    def _draw_diamond(self, cr):
        """
        Helper function to draw diamond shape for shared and composite
        aggregations.
        """
        cr.move_to(20, 0)
        cr.line_to(10, -6)
        cr.line_to(0, 0)
        cr.line_to(10, 6)
        #cr.line_to(20, 0)
        cr.close_path()


    def draw_head_composite(self, context):
        """
        Draw a closed diamond on the line end to indicate composite
        aggregation at association head.
        """
        cr = context.cairo
        self._draw_diamond(cr)
        context.cairo.fill_preserve()
        cr.stroke()
        cr.move_to(20, 0)


    def draw_tail_composite(self, context):
        """
        Draw a closed diamond on the line end to indicate composite
        aggregation at association tail.
        """
        cr = context.cairo
        cr.line_to(20, 0)
        cr.stroke()
        self._draw_diamond(cr)
        cr.fill_preserve()
        cr.stroke()


    def draw_head_shared(self, context):
        """
        Draw an open diamond on the line end to indicate shared aggregation
        at association head.
        """
        cr = context.cairo
        self._draw_diamond(cr)
        cr.move_to(20, 0)


    def draw_tail_shared(self, context):
        """
        Draw an open diamond on the line end to indicate shared aggregation
        at association tail.
        """
        cr = context.cairo
        cr.line_to(20, 0)
        cr.stroke()
        self._draw_diamond(cr)
        cr.stroke()


    def draw_head_navigable(self, context):
        """
        Draw a normal arrow to indicate association end navigability at
        association head.
        """
        cr = context.cairo
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
        cr.stroke()
        cr.move_to(0, 0)


    def draw_tail_navigable(self, context):
        """
        Draw a normal arrow to indicate association end navigability at
        association tail.
        """
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)


    def draw_head_undefined(self, context):
        """
        Draw nothing to indicate undefined association end at association
        head.
        """
        context.cairo.move_to(0, 0)


    def draw_tail_undefined(self, context):
        """
        Draw nothing to indicate undefined association end at association
        tail.
        """
        context.cairo.line_to(0, 0)


class ClassBox(Box):

    '''
    This class represents class on the canvas
    '''

    def __init__(self, name, width=100, height=100):
        super(ClassBox, self).__init__(width, height)
        self.name = name

    def draw(self, context):
        super(ClassBox, self).draw(context)
        c = context.cairo
        x,y = self._central_handle.pos
        text_align(c, x, y, str(self.name), 0, 0)

    def add_moveable_handle(self, canvas, snd_obj):
        handle = Handle(strength=STRONG)
        handle.visible = True
        handle.pos = self.width/2, self.height
        port = PointPort(handle.pos)
        self._ports.append(port)
        self._handles.append(handle)

        c = EquationConstraint(
                lambda x, y : max(math.pow(x-self.width/2,2),
                                  math.pow(y-self.width/2,2)) -
                              math.pow(self.width/2, 2),
                    x=handle.pos[0],
                    y=handle.pos[1]
                )

        sx, sy = self.matrix[4], self.matrix[5]
        fx, fy = snd_obj.matrix[4], snd_obj.matrix[5]
        # count distance between nodes
        dx, dy = fx - sx, fy - sy

        from gaphas.solver import Projection, Variable

        v1, v2 = self.get_centeral_position()
        p1, p2 = Variable(v1+dx), Variable(v2+dy)

        s = LineConstraint(
            (
                self.get_centeral_position(),
                (p1, p2)
            ),
            handle.pos)

        canvas.solver.add_constraint(c)
        #canvas.solver.add_constraint(s)

        return handle, port

def set_association(canvas, o1, o2, props):
    '''
    Make connection between two canvas objects
    @author Jan Vorcak <vorcak@mail.muni.cz>
    @param canvas - canvas on which we will draw
    @param o1 - frist ClassBox to be associated
    @param o2 - second ClassBox to be associated
    @param props - properties of association
    '''

    line = AssociationLine(props)
    for handle in line.handles():
        handle.visible = False

    canvas.add(line)

    h1, p1 = o1.add_moveable_handle(canvas, o2)
    h2, p2 = o2.add_moveable_handle(canvas, o1)

    connector = Connector(line, line.handles()[0])
    connector.connect(ConnectionSink(o1, p1))

    connector = Connector(line, line.handles()[1])
    connector.connect(ConnectionSink(o2, p2))


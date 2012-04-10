from gaphas.item import Element, NW, SW, NE, SE, Line
from gaphas.connector import Handle, PointPort
from gaphas.solver import STRONG, VERY_WEAK, VERY_STRONG
from gaphas.canvas import CanvasProjection
from gaphas.util import text_align, text_extents

from gpylint.canvas.constraints import HandlesConstraint


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

    def add_central_handle(self):
        self._central_handle = Handle(strength=STRONG)
        self._central_handle.visible = False
        self._central_handle.pos = self.width / 2.0, self.height / 2.0
        self._ports.append(PointPort(self._central_handle.pos))
        self._handles.append(self._central_handle)

    def get_canvas_handle(self, handle_type='central'):
        '''
        Return canvas projection of the specified handle
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        @param handle_type - type of the handle
                handle_type should be one of the
                ['central', 'NW', 'NE', 'SW', 'SE']
        '''
        handle_dict = {
            'central': self._central_handle,
            'NW': self._handles[NW],
            'NE': self._handles[NE],
            'SW': self._handles[SW],
            'SE': self._handles[SE]
        }
        assert handle_type in handle_dict.keys()
        handle = handle_dict[handle_type]

        return CanvasProjection(handle.pos, self)

    def draw(self, context):
        c = context.cairo
        nw = self._handles[NW].pos
        c.rectangle(nw.x, nw.y, self.width, self.height)
        if context.hovered:
            c.set_source_rgba(.8,.8,1, .8)
        else:
            c.set_source_rgba(.96, .82, 0.65)
        c.fill()
        c.set_source_rgba(0,0,0)
        c.rectangle(nw.x, nw.y, self.width, self.height)
        c.rectangle(nw.x, nw.y, self.width, 20)
        c.stroke()


class AssociationLine(Line):

    def __init__(self, props):
        '''
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        @param props - properties passed to the line from scanner
        '''
        super(AssociationLine, self).__init__()
        self.props = props
        for handle in self._handles:
            handle.visible = False
            handle.moveable = False

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

    def __init__(self, props, width=100, height=100):
        super(ClassBox, self).__init__(width, height)
        self.properties = props

    filepath = property(lambda x: x.properties['filepath'])
    title = property(lambda x: x.properties['title'])
    lineno = property(lambda x: x.properties['lineno'])

    def draw(self, context):
        # count the size of the Box
        self.width, self.height = text_extents(context.cairo, \
                str(self.title))

        # add some padding
        self.width += 50
        self.height += 50

        # now we have position so we can add central handle and draw object
        self.add_central_handle()

        super(ClassBox, self).draw(context)
        c = context.cairo
        x,y = self._central_handle.pos
        text_align(c, x, 10, str(self.title), 0, 0)

    def _create_handle_and_port(self):
        handle = Handle(strength=VERY_STRONG)
        handle.visible = False
        handle.pos = 0, 0
        port = PointPort(handle.pos)
        return handle, port

    def add_moveable_handle(self, canvas, snd_obj):
        projections = []
        ports = []
        for obj in [self, snd_obj]:
            handle, port = self._create_handle_and_port()
            obj._ports.append(port)
            obj._handles.append(handle)
            hp = CanvasProjection(handle.pos, obj)
            projections.append(hp)
            ports.append(port)

        # function is given a list of projections
        # the first one is self projection, snd_one is snd_obj's projection
        c = HandlesConstraint(o1=self, o2=snd_obj, hp=projections)
        canvas.solver.add_constraint(c)

        return ports

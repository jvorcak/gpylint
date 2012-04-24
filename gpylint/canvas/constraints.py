from gaphas.constraint import Constraint, _update

class HandlesConstraint(Constraint):

    '''
    Init the HandlesConstraint
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    @param self
    @param o1 - first ClassBox object
    @param o2 - second ClassBox object
    @param hp - list of handles (their canvas projections), positions of these
                objects should be updated
                list = [o1's handle, o2's handle]
    '''
    def __init__(self, o1=None, o2=None, hp=None):
        super(HandlesConstraint, self).__init__(hp[0][0], hp[0][1],
                hp[1][0], hp[1][1])
        self.o1 = o1
        self.o2 = o2
        self.hp = hp

    def solve_for(self, var):
        self._solve_for(self.o1, self.hp[0])
        self._solve_for(self.o2, self.hp[1])

    def _solve_for(self, obj, updated_pos):
        two_boxes_line = (self.o1.get_canvas_handle().pos, \
                self.o2.get_canvas_handle().pos)

        NW = obj.get_canvas_handle('NW')
        NE = obj.get_canvas_handle('NE')
        SW = obj.get_canvas_handle('SW')
        SE = obj.get_canvas_handle('SE')

        point = get_cross_point(two_boxes_line, (NE, NW)) or \
                get_cross_point(two_boxes_line, (SE, SW)) or \
                get_cross_point(two_boxes_line, (SW, NW)) or \
                get_cross_point(two_boxes_line, (NE, SE))

        if point:
            _update(updated_pos[0], point[0])
            _update(updated_pos[1], point[1])

def get_cross_point(line1, line2):
    '''
    Return cross point of two line segments
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    @param line1 - tuple of first two positions defining first line segment
    @param line2 - tuple of second two positions defining second line segments
    @return Tuple of floats - cross point of two line segments
            None - if lines are parallel or not crossed in selected intervals
    '''

    # init variables
    p1, p2 = line1
    p3, p4 = line2

    a,b,c,d,e,f,g,h = p1[0].value, p1[1].value, p2[0].value, p2[1].value, \
            p3[0].value, p3[1].value, p4[0].value, p4[1].value

    # check if lines are parallel
    if (a-c)*(f-h) - (b-d)*(e-g) == 0:
        return None

    # get y from parametric equations
    y = (b*(c-a)*(h-f) - a*(d-b)*(h-f) - f*(g-e)*(d-b) + e*(d-b)*(h-f))/\
            ((c-a)*(h-f)-(g-e)*(d-b))
    if h-f != 0:
        x = e+(g-e)*(y-f)/(h-f)
        ty = (y-f)/(h-f)
    if d-b != 0:
        x = a+(c-a)*(y-b)/(d-b)
        ty = (y-b)/(d-b)

    if c-a != 0:
        tx = (x-a)/(c-a)

    if g-e != 0:
        tx = (x-e)/(g-e)

    # check if tx and ty belongs to <0,1>, since we check cross point of
    # line segments
    if not (0 <= tx <= 1):
        return None

    if not (0 <= ty <= 1):
        return None

    return x, y

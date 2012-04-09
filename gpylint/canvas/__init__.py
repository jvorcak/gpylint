'''
This modules is responsible for drawing classes and modules on canvas
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

from gpylint.canvas.items import AssociationLine
from gaphas.aspect import Connector, ConnectionSink


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
        handle.visible = True

    canvas.add(line)

    ports = o1.add_moveable_handle(canvas, o2)

    connector = Connector(line, line.handles()[0])
    connector.connect(ConnectionSink(o1, ports[0]))

    connector = Connector(line, line.handles()[1])
    connector.connect(ConnectionSink(o2, ports[1]))


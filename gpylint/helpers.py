'''
Helper functions
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

def get_pretty_name(name):
    '''
    Get name of the pylint checker and return pretty name
    '''
    name = name.replace('_', ' ')
    return name.capitalize()

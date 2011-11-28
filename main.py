#!/usr/bin/env python
'''
This is the module which wrapps GUI functionality and executes main gtk Window
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

import os
import re

from gi.repository import Gtk
from pylint.lint import Run
from pylint.reporters.text import TextReporter

from editor import GeditEditor
from editor import VimEditor

PYLINT_MSG=re.compile(r'([A-Z]?):([0-9]*):(.*):(.*)')

class Window:
    '''
    This class maps actions from xml to it's methods
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''
    def __init__(self):
        '''
        Initialize builder class and reads objects from xml
        '''
        self.builder = Gtk.Builder()
        self.builder.add_from_file('main.xml')
        self.window = self.builder.get_object('window')
        self.paned = self.builder.get_object('paned')
        self.code_view = self.builder.get_object('code_view')
        self.project_view = self.builder.get_object('project_view')
        self.project_view_store = self.builder.get_object('project_store')
        self.notebook = self.builder.get_object('notebook')

        self.treestore = Gtk.TreeStore(str, str)
        self.project_view.set_model(self.treestore)
        column = Gtk.TreeViewColumn("title", Gtk.CellRendererText(), text=0)
        self.project_view.append_column(column)

        # exit on close
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()

        self.builder.connect_signals(self)
        Gtk.main()

    def open_project(self, menu_item):
        '''
        Open project and load project path
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''

        dialog = Gtk.FileChooserDialog("Title", self.window,\
                Gtk.FileChooserAction.SELECT_FOLDER,\
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,\
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.project_path = dialog.get_filename()
            self.load_tree_view()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def load_tree_view(self):
        '''
        Render project directory in tree view
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''

        parents = {}
        for dir, dirs, files in os.walk(self.project_path):
            for subdir in dirs:
                full_path = os.path.join(dir, subdir)
                parents[full_path] = \
                        self.treestore.append(parents.get(dir, None), [subdir,\
                        full_path])
            for item in files:
                self.treestore.append(parents.get(dir, None), [item,\
                        os.path.join(dir, item)])

    def file_clicked(self, treeview, path, view_column):
        '''
        This method is called when user tries to open a file in the editor
        This file is opened in the noteboook
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        tree_iter = self.treestore.get_iter(path)
        filename = self.treestore.get_value(tree_iter, 0)
        filepath = self.treestore.get_value(tree_iter, 1)

        self.current_file = (filename, filepath)

        # todo check whether file exists
        frame = Gtk.Frame()
        self.editor = GeditEditor(filename, filepath)
        frame.add(self.editor.get_component())
        frame.show()

        self.notebook.append_page(frame, Gtk.Label(filename))

    def run_pylint(self, parent):
        '''
        This method runs pylint agains the currently opened file
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        filename, filepath = self.current_file
        output = PylintContext()
        Run(['--reports=n', filepath], reporter=TextReporter(output), exit=False)
        self.editor.show_pylint_output(output)


class PylintContext(object):

    def __init__(self):
        self.content = []
        self.current = 0

    def write(self, msg):
        search = PYLINT_MSG.search(msg)
        if search:
            self.content.append(search.groups())

    def __iter__(self):
        return self

    def next(self):
        if self.current >= len(self.content):
            self.current = 0
            raise StopIteration
        else:
            self.current += 1
            return self.content[self.current - 1]

if __name__ == '__main__':
    w = Window()

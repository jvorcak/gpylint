#!/usr/bin/env python
'''
This is the module which wrapps GUI functionality and executes main gtk Window
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

import os
import cPickle as pickle

from gi.repository import Gtk
from ConfigParser import ConfigParser
from pylint.lint import Run

# gaphas usage
from gaphas import Canvas, GtkView

# gpylint usage
from gpylint.editor import GeditEditor, VimEditor, ignored_tags
from gpylint.scanner import ScanProject
from gpylint.reporters import EditorReporter

config=ConfigParser()
config.read('config.ini')

class CodeWindow:
    '''
    Source code window
    Author: Jan Vorcak <vorcak@mail.muni.cz>
    '''
    def __init__(self, filename, filepath):
        '''
        Initialize builder class and reads objects from xml
        '''
        self._builder = Gtk.Builder()
        self._builder.add_from_file('windows/code_window.xml')
        self._window = self._builder.get_object('code_window')
        self._code_frame = self._builder.get_object('code_frame')
        self._builder.connect_signals(self)
        self._filename = filename
        self._filepath = filepath
        self._editor = GeditEditor(filename, filepath)
        self._code_frame.add(self._editor.get_component())

        self._window.set_title("%s : %s" % (filename, filepath))

    def show_all(self):
        self._window.show_all()

    def run_pylint(self, parent):
        '''
        This method runs pylint agains the currently opened file
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        Run(['--reports=n', self._filepath], reporter=EditorReporter(self._editor), \
                exit=False)

    def save(self, parent):
        raise NotImplementedError

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
        self.builder.add_from_file('windows/main.xml')
        self.window = self.builder.get_object('window')
        self.paned_main = self.builder.get_object('paned_main')
        self.project_view = self.builder.get_object('project_view')

        self.treestore = Gtk.TreeStore(str, str)
        self.project_view.set_model(self.treestore)
        column = Gtk.TreeViewColumn("Title", Gtk.CellRendererText(), text=0)
        self.project_view.append_column(column)

        # set graph as a second item in the main paned
        self.view = GtkView()
        self.view.canvas = Canvas()
        self.paned_main.add2(self.view)

        # exit on close
        self.window.connect("delete-event", self.exit)
        self.window.show_all()

        self.builder.connect_signals(self)

        # init lastest project
        if config.has_option('project', 'project_path'):
            self.project_path = config.get('project', 'project_path')
            self.load_tree_view()

        # scan project and display UML on the canvas
        # TODO threading
        ScanProject(self.view, [self.project_path])

        try:
            with open('.ignored_tags', 'r') as f:
                try:
                    errors=pickle.load(f)
                    ignored_tags.load_errors(errors)
                except EOFError:
                    pass
        except IOError:
            pass

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

            # add project_path to config to that program starts with latest
            # project opened
            if not config.has_section('project'):
                config.add_section('project')
            config.set('project', 'project_path', self.project_path)

            self.load_tree_view()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def load_tree_view(self):
        '''
        Render project directory in tree view
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''

        self.treestore.clear()
        parents = {}
        for dr, dirs, files in os.walk(self.project_path):
            for subdir in dirs:
                full_path = os.path.join(dr, subdir)
                parents[full_path] = \
                        self.treestore.append(parents.get(dr, None), [subdir,\
                        full_path])
            for item in files:
                self.treestore.append(parents.get(dr, None), [item,\
                        os.path.join(dr, item)])

    def file_clicked(self, treeview, path, view_column):
        '''
        This method is called when user tries to open a file in the editor
        This file is opened in the noteboook
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        tree_iter = self.treestore.get_iter(path)
        filename = self.treestore.get_value(tree_iter, 0)
        filepath = self.treestore.get_value(tree_iter, 1)

        # todo check whether file exists
        window = CodeWindow(filename, filepath)
        window.show_all()

    def zoom_in(self, button):
        '''
        Zoom in the canvas
        '''
        self.view.zoom(1.2)

    def zoom_out(self, button):
        '''
        Zoom out the canvas
        '''
        self.view.zoom(1/1.2)

    def exit(self, event, data):
        '''
        Close the program and save the path to config
        '''

        # pickle ignored tags to a file
        with open('.ignored_tags', 'w') as f:
            pickle.dump(ignored_tags.ignored, f)

        #TODO fix closing the program
        with open('config.ini', 'w') as f:
            config.write(f)

        Gtk.main_quit(event, data)


if __name__ == '__main__':
    w = Window()

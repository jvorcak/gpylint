#!/usr/bin/env python
'''
This is the module which wrapps GUI functionality and executes main gtk Window
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''
import os
import cPickle as pickle
import argparse
import logging

parser = argparse.ArgumentParser(description='GPylint help')
parser.add_argument('path', default=None, nargs='?', help='Path of the project to be scanned')
args = parser.parse_args()

from gi import require_version
from gi.repository import Gtk, Gdk, GObject
require_version('Gtk', '3.0')

# gaphas usage
from gaphas import Canvas, GtkView
from gaphas.tool import ToolChain, HoverTool, ConnectHandleTool, PanTool, \
        ZoomTool, ItemTool, TextEditTool, RubberbandTool

# gpylint usage
from gpylint.editor import ignored_tags
from gpylint.scanner import ScanProject, BlackList
from gpylint.lint import ProjectLinter
from gpylint.reporters import CanvasReporter
from gpylint.canvas.tools import OpenEditorTool
from gpylint.windows import WindowManager, SettingsWindow
from gpylint.settings.PylintMessagesManager import PylintMessagesManager
from gpylint.settings.GeneralSettingsManager import GeneralSettingsManager

GObject.threads_init()
Gdk.threads_init()

wm = WindowManager()

pmm = PylintMessagesManager()
gsm = GeneralSettingsManager()

logger = logging.getLogger('main')
hdlr = logging.FileHandler('/var/tmp/gpylint.log', 'w')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

logger.info('Initializing application')

try:
    with open('.ignored_files', 'r') as f:
        try:
            logger.info('Parsing blacklist from cPickled data')
            BlackList.blacklist=pickle.load(f)
            logger.info('Loaded BlackList = %s' % BlackList().blacklist)
        except EOFError:
            pass
except IOError:
    pass

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
        self.paned_left = self.builder.get_object('paned_left')
        self.project_view = self.builder.get_object('project_view')
        self.diagram_spinner = self.builder.get_object('diagram_spinner')
        self.scanning_bar = self.builder.get_object('scanning_bar')
        self.canvas_area = self.builder.get_object('canvas_area')
        self.refresh_diagram = self.builder.get_object('refresh_diagram')

        self.treestore = Gtk.TreeStore(str, str)
        self.project_view.set_model(self.treestore)
        renderer = Gtk.CellRendererText()


        def renderId(treeviewcolumn, renderer, model, iter, data):
            if model.get_value(iter,1) in BlackList.blacklist:
                renderer.set_property('foreground', 'red')
            else:
                renderer.set_property('foreground', 'black')


        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        column.set_cell_data_func(renderer, renderId)
        self.project_view.append_column(column)
        self.project_view.connect('button_release_event', self.popup_show)

        action_group = Gtk.ActionGroup('actions')

        self.ignore_action = Gtk.Action('Ignore', 'Ignore', None, Gtk.STOCK_STOP)
        self.ignore_action.connect('activate', self.ignore_file)

        self.dont_ignore_action = Gtk.Action('Dontignore', 'Don\'t ignore', None, Gtk.STOCK_STOP)
        self.dont_ignore_action.connect('activate', self.dont_ignore_file)

        action_group.add_action(self.ignore_action)
        action_group.add_action(self.dont_ignore_action)

        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string("""
        <ui>
         <popup name='PopupMenu'>
          <menuitem action='Ignore' />
          <menuitem action='Dontignore' />
         </popup>
        </ui>
        """)
        uimanager.insert_action_group(action_group)

        self.popup = uimanager.get_widget("/PopupMenu")


        # set graph as a second item in the main paned
        self.view = GtkView()
        self.view.canvas = Canvas()
        self.view.tool = ToolChain(self.view). \
            append(OpenEditorTool()). \
            append(HoverTool()). \
            append(ConnectHandleTool()). \
            append(PanTool()). \
            append(ZoomTool()). \
            append(ItemTool()). \
            append(TextEditTool()). \
            append(RubberbandTool())

        # add minimized view
        #self.minimized_view = GtkView()
        #self.minimized_view.canvas = self.view.canvas
        #self.minimized_view.zoom(1/3.)
        #self.paned_left.add2(self.minimized_view)

        self.canvas_area.append_page(self.view, None)
        self.view.show()

        # exit on close
        self.window.connect("delete-event", self.exit)
        self.window.maximize()
        self.window.show()
        self.scanning_bar.set_visible(False)

        self.builder.connect_signals(self)

        self.project_path = None
        self.canvas_area.set_current_page(1)

        if args.path:
            self.project_path = args.path
            self.load_tree_view()
        elif gsm.get(gsm.PROJECT_PATH):
            self.project_path = gsm.get(gsm.PROJECT_PATH)
            self.load_tree_view()

        logger.info('Application GUI sucesfully loaded')

        # scan project and display UML on the canvas
        if self.project_path:
            self.canvas_area.set_current_page(0)
            logger.info('Starting to scan project %s' % self.project_path)
            t=ScanProject(self.view, [self.project_path], self.show_graph)
            t.start()

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

    def check_project(self, button):
        self.scanning_bar.set_visible(True)
        pylintrc = None
        plugins = []
        linter = ProjectLinter()
        linter.set_project_path(self.project_path)
        linter.init_linter(CanvasReporter(self.scanning_bar), pylintrc)
        linter.load_default_plugins()
        linter.load_plugin_modules(plugins)
        linter.read_config_file()
        linter.load_config_file()
        linter.start()

    def ignore_file(self, event):
        treestore, treepaths = self.project_view.get_selection().get_selected_rows()
        for treepath in treepaths:
            iter = treestore.get_iter(treepath)
            BlackList.blacklist.append(treestore.get_value(iter, 1))

    def dont_ignore_file(self, event):
        treestore, treepaths = self.project_view.get_selection().get_selected_rows()
        for treepath in treepaths:
            iter = treestore.get_iter(treepath)
            BlackList.blacklist.remove(treestore.get_value(iter, 1))

    def popup_show(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3:
            self.dont_ignore_action.set_visible(False)
            self.ignore_action.set_visible(False)
            treestore, treepaths = self.project_view.get_selection().get_selected_rows()
            for treepath in treepaths:
                iter = treestore.get_iter(treepath)
                if treestore.get_value(iter, 1) in BlackList.blacklist:
                    self.dont_ignore_action.set_visible(True)
                else:
                    self.ignore_action.set_visible(True)
            self.popup.popup(None, None, None, None, event.button, event.time)    


    def refresh_clicked(self, button):
        self.canvas_area.set_current_page(0)
        for item in self.view.canvas.get_all_items():
            self.view.canvas.remove(item)
        t=ScanProject(self.view, [self.project_path], self.show_graph)
        t.start()

    def show_graph(self):
        self.canvas_area.set_current_page(1)

    def open_settings(self, menu_item):
        '''
        Display settings window
        '''
        window = SettingsWindow()
        window.show_all()

    def open_project(self, menu_item):
        '''    def exit(self, event, data):
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

            if os.path.exists(self.project_path + "/__init__.py"):
                # add project_path to config to that program starts with latest
                # project opened
                gsm.set(gsm.PROJECT_PATH, self.project_path)

                self.load_tree_view()
            else:
                md = Gtk.MessageDialog(None, 0, \
                        Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, \
                        "Selected directory does not contain valid python project")
                md.run()
                md.destroy()
                dialog.destroy()
                return
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
        self.refresh_clicked(None)

    def load_tree_view(self):
        '''
        Render project directory in tree view
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''

        ignored_suffixes = ['.pyc', '.pyo']

        self.treestore.clear()
        parents = {}
        for dr, dirs, files in os.walk(self.project_path):
            for subdir in dirs:
                full_path = os.path.join(dr, subdir)
                parents[full_path] = \
                        self.treestore.append(parents.get(dr, None), [subdir,\
                        full_path])
            for item in files:
                if True in [item.endswith(x) for x in ignored_suffixes]:
                    continue
                self.treestore.append(parents.get(dr, None), [item,\
                        os.path.join(dr, item)])

    def file_clicked(self, treeview, path, view_column):
        '''
        This method is called when user tries to open a file in the editor
        This file is opened in the noteboook
        Author: Jan Vorcak <vorcak@mail.muni.cz>
        '''
        tree_iter = self.treestore.get_iter(path)
        filepath = self.treestore.get_value(tree_iter, 1)

        # TODO check whether file exists
        # TODO remove duplicated code (OpenEditorTool)
        window = wm.get_window(filepath)
        window.show_all()
        window.present()

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

    def quit(self, button):
        self._quit()

    def exit(self, event, data):
        '''
        Close the program and save the path to config
        '''
        self._quit()


    def _quit(self):

        # pickle ignored tags to a file
        with open('.ignored_tags', 'w') as f:
            pickle.dump(ignored_tags.ignored, f)

        with open('.ignored_files', 'w') as f:
            pickle.dump(BlackList.blacklist, f)

        gsm.save()
        pmm.save()

        Gtk.main_quit(None, None)

if __name__ == '__main__':
    w = Window()
